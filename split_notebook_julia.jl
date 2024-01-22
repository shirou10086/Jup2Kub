using NBInclude
using Pkg
#split notebook for julia languages, still under development
# Extract imports from a notebook cell
function extract_imports(cell)
    imports = []
    for line in split(cell, '\n')
        if startswith(line, "using ") || startswith(line, "import ")
            push!(imports, strip(line))
        end
    end
    return imports
end

# Extract file paths used in the notebook
function extract_file_paths(cell)
    files = []
    # Add logic to extract file paths, similar to Python's implementation
    return files
end

# Save each cell to a separate file
function save_cells_to_files(notebook, output_directory, dependencies)
    mkpath(output_directory, mode=0o775)
    dependencies_block = join(dependencies, "\n") * "\n\n"

    valid_cell_index = 0
    for cell in notebook
        if cell.cell_type == "code" && !isempty(strip(cell.source))
            cell_file_path = joinpath(output_directory, "cell_$(valid_cell_index).jl")
            write(cell_file_path, dependencies_block * cell.source)
            valid_cell_index += 1
        end
    end

    println("$(valid_cell_index) non-empty cells have been saved to separate files in $(output_directory), with dependencies included.")
end

# Print environment information
function get_environment_info()
    return Pkg.status()
end

# Save requirements (Project.toml and Manifest.toml)
function save_requirements(output_directory)
    Pkg.activate(output_directory)
    Pkg.resolve()
    println("Requirements saved to $(output_directory)/Project.toml and Manifest.toml")
end

# Process the notebook
function process_notebook(notebook_path, output_directory)
    notebook = nbinclude(notebook_path)

    dependencies, file_paths = Set{String}(), Set{String}()

    for cell in notebook
        append!(dependencies, extract_imports(cell.source))
        append!(file_paths, extract_file_paths(cell.source))
    end

    println("Dependencies found in the notebook:")
    for dep in dependencies
        println(dep)
    end

    println("\nFile paths found in the notebook:")
    for path in file_paths
        println(path)
    end

    save_cells_to_files(notebook, output_directory, dependencies)
    println("Non-empty cells have been saved to separate files in $(output_directory), with dependencies included.")

    println("\nEnvironment information:")
    println(get_environment_info())

    save_requirements(output_directory)
end

# Example usage
notebook_path = "./example/julia_notebook.ipynb"  # Replace with your notebook path
output_directory = "./example/output_julia"      # Replace with your desired output directory
process_notebook(notebook_path, output_directory)
