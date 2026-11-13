# Independent R cross-check of the confirmatory survey estimates (audit item: "reproduce in R or Stata").
#
# Re-estimates, with the R `survey` and `mitools` packages, the prespecified contrasts of
#   * Paper 1 (NLSY97): theta(12..16) and Delta(16 - 12) for mothers and fathers -- primary (m = 40 imputations) and S2 (complete cases);
#   * B2 (HSLS:09): theta9, theta11 and their difference -- primary (m = 20 imputations) and S2 (complete cases),
# and compares them with the official Python estimates in crosscheck/python_reference.json.
#
# Independent here: model fitting, design-based variance (Taylor linearization with strata/PSU and domain estimation;
# BRR with 200 replicates), linear contrasts and Rubin / Barnard-Rubin pooling. NOT independent: data preparation and
# the imputations, which are exported by scripts/export_crosscheck_data.py from the official seeded runs.
#
# Usage (from the turning-point-project folder):
#   Rscript crosscheck/crosscheck.R [data folder, default data/crosscheck]
# Requires: install.packages(c("survey", "mitools", "jsonlite"))
# Writes: outputs/crosscheck_r/crosscheck_results.csv and outputs/crosscheck_r/crosscheck_summary.txt

suppressPackageStartupMessages({
  library(survey)
  library(mitools)
  library(jsonlite)
})
options(survey.lonely.psu = "fail")  # the Python code also refuses single-PSU strata

args <- commandArgs(trailingOnly = TRUE)
data_dir <- if (length(args) >= 1) args[1] else "data/crosscheck"
out_dir <- "outputs/crosscheck_r"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
ref <- fromJSON("crosscheck/python_reference.json", simplifyVector = FALSE)

TOL_EST <- 1e-6  # relative tolerance (scale max(1, |x|)) for estimates and CI limits
TOL_SE <- 1e-6   # relative tolerance for standard errors
rows <- list()

compare <- function(study, analysis, quantity, est, se, df, py) {
  t_r <- qt(0.975, df)
  r <- data.frame(study = study, analysis = analysis, quantity = quantity,
                  est_r = est, est_py = py$estimate, se_r = se, se_py = py$se,
                  df_r = df, df_py = py$df,
                  ci_low_r = est - t_r * se, ci_low_py = py$ci_low,
                  ci_high_r = est + t_r * se, ci_high_py = py$ci_high)
  r$est_absdiff <- abs(r$est_r - r$est_py)
  r$se_reldiff <- abs(r$se_r - r$se_py) / r$se_py
  r$ci_absdiff <- pmax(abs(r$ci_low_r - r$ci_low_py), abs(r$ci_high_r - r$ci_high_py))
  r$pass <- r$est_absdiff <= TOL_EST * pmax(1, abs(r$est_py)) &
            r$se_reldiff <= TOL_SE &
            r$ci_absdiff <= TOL_EST * pmax(1, abs(r$ci_low_py), abs(r$ci_high_py))
  rows[[length(rows) + 1]] <<- r
}

MITOOLS_DF <- list()
MI_DF_PUBLISHED <- list()
pool <- function(ests, vars, df_complete) {
  # Rubin's rules via mitools::MIcombine. The small-sample df is computed here with the published Barnard & Rubin (1999)
  # formula, nu_obs = (nu_com + 1) / (nu_com + 3) * nu_com * (1 - gamma), gamma = (1 + 1/m) B / T. mitools uses
  # Ubar / (Ubar + B) in place of (1 - gamma) = Ubar / (Ubar + (1 + 1/m) B), which gives slightly larger df; its df are
  # kept in MITOOLS_DF and reported in the summary for transparency.
  mi <- MIcombine(results = ests, variances = vars, df.complete = df_complete)
  m <- length(ests)
  U <- Reduce(`+`, lapply(vars, function(v) diag(as.matrix(v)))) / m
  B <- apply(do.call(rbind, ests), 2, var)
  T <- U + (1 + 1 / m) * B
  stopifnot(isTRUE(all.equal(unname(T), unname(diag(vcov(mi))), tolerance = 1e-12)))
  gam <- (1 + 1 / m) * B / T
  nu_old <- (m - 1) / gam^2
  nu_obs <- (df_complete + 1) / (df_complete + 3) * df_complete * (1 - gam)
  MITOOLS_DF[[length(MITOOLS_DF) + 1]] <<- mi$df
  MI_DF_PUBLISHED[[length(MI_DF_PUBLISHED) + 1]] <<- 1 / (1 / nu_old + 1 / nu_obs)
  list(est = coef(mi), se = sqrt(T), df = 1 / (1 / nu_old + 1 / nu_obs), df_mitools = mi$df)
}

# ------------------------------------------------------------------ Paper 1 (NLSY97), Taylor linearization
AGES <- 12:16
P1_CONTRASTS <- c(lapply(AGES, function(a) c(s = 1, sxa = a - 14)), list(c(sxa = 4)))
names(P1_CONTRASTS) <- c(paste0("theta_", AGES), "delta_16_vs_12")

p1_contrasts <- function(d, covs_all) {
  live <- d$dom == 1
  # same rule as the Python code: drop covariates constant among in-domain rows
  covs <- covs_all[vapply(covs_all, function(v) length(unique(d[[v]][live])) > 1, logical(1))]
  d$sxa <- d$s * d$agec
  d$wdes <- ifelse(live, d$w, 1)  # out-of-domain rows keep the design; subset() below zero-weights them
  des <- svydesign(ids = ~psu, strata = ~strata, weights = ~wdes, nest = TRUE, data = d)
  f <- as.formula(paste("hgc ~ s + agec + sxa", if (length(covs)) paste("+", paste(covs, collapse = " + ")) else ""))
  fit <- svyglm(f, design = subset(des, dom == 1))
  if (any(is.na(coef(fit)))) stop("aliased coefficients: ", paste(names(coef(fit))[is.na(coef(fit))], collapse = ", "))
  sc <- svycontrast(fit, P1_CONTRASTS)
  list(est = coef(sc), var = vcov(sc), design_df = degf(des))
}

p1 <- ref$paper1
for (who in c("mother", "father")) {
  covs <- unlist(p1[[who]]$covariates)
  cat("Paper 1,", who, ": primary (", p1$m, "imputations)\n")
  d <- read.csv(file.path(data_dir, paste0("p1_", who, "_imputed.csv.gz")))
  res <- lapply(split(d, d$imp), p1_contrasts, covs_all = covs)
  stopifnot(all(vapply(res, `[[`, numeric(1), "design_df") == p1$design_df))
  pl <- pool(lapply(res, `[[`, "est"), lapply(res, `[[`, "var"), p1$design_df)
  for (j in seq_along(P1_CONTRASTS)) {
    q <- names(P1_CONTRASTS)[j]
    py <- Filter(function(x) x$quantity == q, p1[[who]]$primary)[[1]]
    compare("Paper 1 NLSY97", paste(who, "primary (MI)"), q, pl$est[j], pl$se[j], pl$df[j], py)
  }
  cat("Paper 1,", who, ": S2 complete cases\n")
  cc <- read.csv(file.path(data_dir, paste0("p1_", who, "_cc.csv.gz")))
  r <- p1_contrasts(cc, covs)
  for (j in seq_along(P1_CONTRASTS)) {
    q <- names(P1_CONTRASTS)[j]
    py <- Filter(function(x) x$quantity == q, p1[[who]]$S2)[[1]]
    compare("Paper 1 NLSY97", paste(who, "S2 complete cases"), q, r$est[j], sqrt(r$var[j, j]), r$design_df, py)
  }
}

# ------------------------------------------------------------------ B2 (HSLS:09), BRR with 200 replicate weights
b2 <- ref$b2
B2_COVS <- unlist(b2$covariates)
wts <- read.csv(file.path(data_dir, "b2_weights.csv.gz"))
REPS <- grep("^W2W1STU[0-9]{3}$", names(wts), value = TRUE)
stopifnot(length(REPS) == b2$n_replicates)

b2_theta <- function(w, data) {
  # Separate models for the grade-9 and grade-11 ratings, each standardized with the (replicate) weight in use.
  keep <- w > 0
  d <- data[keep, ]; w <- w[keep]
  wstd <- function(x) { mu <- sum(w * x) / sum(w); (x - mu) / sqrt(sum(w * (x - mu)^2) / sum(w)) }
  C <- as.matrix(d[, B2_COVS])
  b9 <- lm.wfit(cbind(1, wstd(d$sup9), C), d$ba, w)$coefficients[2]
  b11 <- lm.wfit(cbind(1, wstd(d$sup11), C), d$ba, w)$coefficients[2]
  c(theta9 = unname(b9), theta11 = unname(b11), diff_11_minus_9 = unname(b11 - b9))
}

b2_brr <- function(d) {
  dd <- merge(d, wts, by = "id", sort = TRUE)
  # Standard BRR (no Fay factor); variance centered on the full-sample estimate (mse = TRUE), as in the Python code.
  des <- svrepdesign(data = dd, weights = ~w, repweights = dd[, REPS], type = "BRR",
                     combined.weights = TRUE, mse = TRUE)
  wr <- withReplicates(des, b2_theta)
  list(est = coef(wr), var = vcov(wr))
}

cat("B2: primary (", b2$m, "imputations)\n")
imp <- read.csv(file.path(data_dir, "b2_imputed.csv.gz"))
res <- lapply(split(imp, imp$imp), b2_brr)
pl <- pool(lapply(res, `[[`, "est"), lapply(res, `[[`, "var"), b2$df_complete)
for (j in 1:3) {
  py <- b2$primary[[j]]
  compare("B2 HSLS:09", "primary (MI)", py$quantity, pl$est[j], pl$se[j], pl$df[j], py)
}
cat("B2: S2 complete cases\n")
r <- b2_brr(read.csv(file.path(data_dir, "b2_cc.csv.gz")))
for (j in 1:3) {
  py <- b2$S2[[j]]
  compare("B2 HSLS:09", "S2 complete cases", py$quantity, r$est[j], sqrt(r$var[j, j]), b2$df_complete, py)
}

# ------------------------------------------------------------------ report
out <- do.call(rbind, rows)
write.csv(out, file.path(out_dir, "crosscheck_results.csv"), row.names = FALSE)
fmt <- function(x) formatC(x, format = "e", digits = 1)
lines <- c(
  "Independent R cross-check of confirmatory survey estimates",
  paste("Run:", format(Sys.time(), "%Y-%m-%d %H:%M %Z"), "|", R.version.string,
        "| survey", as.character(packageVersion("survey")), "| mitools", as.character(packageVersion("mitools"))),
  "",
  sprintf("Quantities compared: %d; passed: %d (tolerance %.0e relative)", nrow(out), sum(out$pass), TOL_EST),
  sprintf("Largest |estimate difference|: %s; largest relative SE difference: %s; largest |CI-limit difference|: %s",
          fmt(max(out$est_absdiff)), fmt(max(out$se_reldiff)), fmt(max(out$ci_absdiff))),
  sprintf("Largest |df difference| (pooled Barnard-Rubin df): %s", fmt(max(abs(out$df_r - out$df_py)))),
  sprintf("Note: mitools::MIcombine's own df variant differs from the published Barnard-Rubin df by up to %.2f df (no effect on estimates or SEs).",
          max(unlist(Map(function(a, b) max(abs(a - b)), MITOOLS_DF, MI_DF_PUBLISHED)))),
  "",
  "Prespecified contrasts (R estimate, 95% CI | Python estimate):"
)
key <- out[out$quantity %in% c("theta_14", "delta_16_vs_12", "theta9", "theta11", "diff_11_minus_9"), ]
lines <- c(lines, sprintf("  %-15s %-28s %-16s %9.4f (%8.4f, %8.4f) | %9.4f  %s",
                          key$study, key$analysis, key$quantity, key$est_r, key$ci_low_r, key$ci_high_r, key$est_py,
                          ifelse(key$pass, "PASS", "FAIL")))
lines <- c(lines, "", if (all(out$pass)) "RESULT: all quantities agree within tolerance." else
  "RESULT: DISAGREEMENT -- see crosscheck_results.csv (rows with pass = FALSE).")
writeLines(lines, file.path(out_dir, "crosscheck_summary.txt"))
cat(lines, sep = "\n")
if (!all(out$pass)) quit(status = 1)
