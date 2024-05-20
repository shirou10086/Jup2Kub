library(jsonlite)

# Function to analyze variable usage and track all assignments
track_variables <- function(code) {
    assign_pattern <- "\\b(\\w+)\\s*<-"
    use_pattern <- "\\b(\\w+)\\b"
    for_pattern <- "for\\s*\\((\\w+)\\s+in"
    while_pattern <- "while\\s*\\((\\w+)\\s*"
    repeat_pattern <- "repeat\\s*\\{"

    assigns <- gregexpr(assign_pattern, code, perl = TRUE)
    uses <- gregexpr(use_pattern, code, perl = TRUE)
    fors <- gregexpr(for_pattern, code, perl = TRUE)
    whiles <- gregexpr(while_pattern, code, perl = TRUE)
    repeats <- gregexpr(repeat_pattern, code, perl = TRUE)

    assigned_vars <- unique(regmatches(code, assigns)[[1]])
    used_vars <- unique(regmatches(code, uses)[[1]])
    for_vars <- unique(regmatches(code, fors)[[1]])
    while_vars <- unique(regmatches(code, whiles)[[1]])
    repeat_vars <- unique(regmatches(code, repeats)[[1]])

    assigned_vars <- gsub("\\s*<-\\s*", "", assigned_vars)
    for_vars <- gsub("for\\s*\\(|\\s+in.*", "", for_vars)
    while_vars <- gsub("while\\s*\\(|\\s*\\).*", "", while_vars)
    repeat_vars <- character()  # repeat does not declare variables like for and while

    # Filter out R keywords
    keywords <- c("if", "else", "for", "while", "repeat", "function", "library", "require", "return")
    used_vars <- setdiff(used_vars, c(keywords, for_vars, while_vars, repeat_vars))

    list(global_vars = assigned_vars, used_vars = used_vars, loop_vars = c(for_vars, while_vars))
}

# Function to insert code into R script
insert_code_to_cell <- function(filepath, previous_vars) {
    lines <- readLines(filepath, warn = FALSE)

    # Ensure the last line ends with a newline character
    if (length(lines) == 0 || lines[length(lines)] != "") {
        lines <- c(lines, "")
    }

    code <- paste(lines, collapse = "\n")
    vars <- track_variables(code)

    cell_number <- as.numeric(sub("cell(\\d+)\\.R$", "\\1", basename(filepath)))

    fetch_and_wait_statements <- c()
    if (cell_number > 1) {
        # Find the line number where each variable is assigned
        assignment_lines <- sapply(vars$global_vars, function(var) {
            grep(paste0("\\b", var, "\\s*<-"), lines)
        }, simplify = FALSE)

        for (var in vars$used_vars) {
            if (var %in% previous_vars && !(var %in% vars$loop_vars)) {
                assignment_line <- assignment_lines[[var]]
                first_use_line <- grep(paste0("\\b", var, "\\b"), lines)[1]

                # Fetch the variable only if it is used before being assigned
                if (length(assignment_line) == 0 || first_use_line < assignment_line[1]) {
                    fetch_code <- sprintf("%s <- fetchVarResult('%s', varAncestorCell=%dL, host='results-hub-service.default.svc.cluster.local')", var, var, cell_number - 1)
                    fetch_and_wait_statements <- c(fetch_and_wait_statements, fetch_code)
                }
            }
        }
        fetch_and_wait_statements <- c(fetch_and_wait_statements, sprintf("waitForCell(waitFor=%d, host='results-hub-service.default.svc.cluster.local')", cell_number - 1))
    }

    init_code <- c(
        'options(repos = c(CRAN = "https://cran.r-project.org"))',
        'if (!require("reticulate")) install.packages("reticulate")',
        'library(reticulate)',
        '',
        'use_python("/usr/bin/python3", required = TRUE)',
        'env_name <- "python_env_for_r"',
        'if (!virtualenv_exists(env_name)) virtualenv_create(env_name)',
        'use_virtualenv(env_name, required = TRUE)',
        'py_install(c("grpcio", "grpcio-tools", "protobuf"), envname = env_name)',
        '',
        '# ========== ABOVE SHOULD BE DONE DURING DOCKER BUILDING ==========',
        '',
        '# Source the Python client',
        'source_python("ResultsHubForR.py")',
        ''
    )

    if (!any(grepl("source_python\\(\"ResultsHubForR.py\"\\)", lines))) {
        lines <- c(init_code, lines)
    }

    import_index <- which(grepl("source_python\\(\"ResultsHubForR.py\"\\)", lines))[1]
    lines <- append(lines, fetch_and_wait_statements, after = import_index)

    submit_code <- "\n# SUBMIT CODE START\n"
    submit_code <- paste0(submit_code, sprintf("results_hub <- ResultsHubSubmission(%dL, host='results-hub-service.default.svc.cluster.local')\n", cell_number))
    for (var in vars$global_vars) {
        submit_code <- paste0(submit_code, sprintf("results_hub$addVar('%s', %s)\n", var, var))
    }
    submit_code <- paste0(submit_code, "results_hub$submit()\n")
    submit_code <- paste0(submit_code, sprintf("print('Submission Success for cell %d.')\n", cell_number))
    submit_code <- paste0(submit_code, "# SUBMIT CODE END\n")

    lines <- c(lines, submit_code)

    writeLines(lines, filepath)

    return(vars$global_vars)
}

# Process all cell files in the directory
gen_code_to_all_cells <- function(directory) {
    previous_vars <- c()
    files <- list.files(directory, pattern = "^cell\\d+\\.R$", full.names = TRUE)
    for (filepath in files) {
        previous_vars <- c(previous_vars, insert_code_to_cell(filepath, previous_vars))
    }
}

# Main function
main <- function() {
    args <- commandArgs(trailingOnly = TRUE)
    
    # Default directory is './execution' if no argument is provided
    directory <- ifelse(length(args) > 0, args[1], './execution')
    
    gen_code_to_all_cells(directory)
}

main()
