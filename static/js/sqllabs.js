// SQL Labs main JavaScript file
document.addEventListener("DOMContentLoaded", function () {
  // Initialize SQL.js
  initSqlJs({
    locateFile: (file) =>
      `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.8.0/${file}`,
  })
    .then((SQL) => {
      // Store the SQL.js instance
      window.SQL = SQL;

      // Initialize the database
      initializeDatabase();

      // Set up the editor and form if on exercise page
      if (typeof exercise !== "undefined") {
        setupEditor();

        // Setup either the placeholder form or JS editor based on mode
        if (exercise.allow_js) {
          setupJsEditor();
        } else {
          setupPlaceholderForm();
        }
      }
    })
    .catch((err) => {
      console.error("Error initializing SQL.js:", err);
    });
});

// Global variables
let db = null;
let editor = null;
let jsEditor = null;

/**
 * Initialize the SQL database with the exercise setup code
 */
function initializeDatabase() {
  if (!window.SQL || typeof exercise === "undefined") return;

  try {
    // Create a new database
    db = new window.SQL.Database();

    // Run the setup code
    db.run(exercise.setup_code);

    // Extract and display schema information for the specified tables
    if (exercise.show_tables && exercise.show_tables.length > 0) {
      displayDatabaseSchema();
    }
  } catch (error) {
    console.error("Error initializing database:", error);
  }
}

/**
 * Extract and display database schema for the specified tables
 */
function displayDatabaseSchema() {
  if (!db) return;

  const schemaContainer = document.getElementById("schema-container");
  schemaContainer.innerHTML = "";

  try {
    // For each table in show_tables, get its schema
    exercise.show_tables.forEach((tableName) => {
      // Query the schema
      const tableInfoQuery = `PRAGMA table_info("${tableName}")`;
      const tableInfoResult = db.exec(tableInfoQuery);

      if (tableInfoResult.length > 0) {
        const tableInfo = tableInfoResult[0];

        // Create table element
        const tableDiv = document.createElement("div");
        tableDiv.className = "schema-table mb-4";

        // Table name header
        const tableHeader = document.createElement("h6");
        tableHeader.textContent = tableName;
        tableDiv.appendChild(tableHeader);

        // Create the table structure display
        const tableStructure = document.createElement("table");
        tableStructure.className = "table table-sm";

        // Table header
        const thead = document.createElement("thead");
        const headerRow = document.createElement("tr");
        ["Column", "Type", "PK", "NN", "Default"].forEach((colName) => {
          const th = document.createElement("th");
          th.textContent = colName;
          th.style.fontSize = "0.8rem";
          headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        tableStructure.appendChild(thead);

        // Table body
        const tbody = document.createElement("tbody");

        // For each column in the table
        for (let i = 0; i < tableInfo.values.length; i++) {
          const row = tableInfo.values[i];
          const tr = document.createElement("tr");

          // Column name
          const tdName = document.createElement("td");
          tdName.textContent = row[1]; // Name is at index 1
          tdName.style.fontWeight = "bold";
          tr.appendChild(tdName);

          // Column type
          const tdType = document.createElement("td");
          tdType.textContent = row[2]; // Type is at index 2
          tr.appendChild(tdType);

          // Primary key
          const tdPk = document.createElement("td");
          tdPk.textContent = row[5] === 1 ? "✓" : ""; // PK is at index 5
          tr.appendChild(tdPk);

          // Not null
          const tdNotNull = document.createElement("td");
          tdNotNull.textContent = row[3] === 1 ? "✓" : ""; // NotNull is at index 3
          tr.appendChild(tdNotNull);

          // Default value
          const tdDefault = document.createElement("td");
          tdDefault.textContent = row[4] !== null ? row[4] : ""; // Default is at index 4
          tr.appendChild(tdDefault);

          tbody.appendChild(tr);
        }

        tableStructure.appendChild(tbody);
        tableDiv.appendChild(tableStructure);
        schemaContainer.appendChild(tableDiv);
      }
    });
  } catch (error) {
    console.error("Error displaying schema:", error);
    schemaContainer.innerHTML = `<div class="alert alert-danger">Error loading schema: ${error.message}</div>`;
  }
}

/**
 * Set up the CodeMirror editor
 */
function setupEditor() {
  if (typeof exercise === "undefined" || !exercise.show_query) return;

  const editorElement = document.getElementById("sql-editor");

  // Check if editor element exists
  if (!editorElement) return;

  // Initialize CodeMirror
  editor = CodeMirror(editorElement, {
    value: exercise.base_query,
    mode: "text/x-sql",
    theme: "monokai",
    lineNumbers: true,
    readOnly: true,
  });

  // Resize editor to fit content
  editor.setSize(null, "auto");
}

/**
 * Generate form fields for each placeholder
 */
function setupPlaceholderForm() {
  if (typeof exercise === "undefined") return;

  const placeholderFields = document.getElementById("placeholder-fields");
  if (!placeholderFields) return;

  placeholderFields.innerHTML = "";

  // Check if placeholders exist and is an array
  if (
    !exercise.placeholders ||
    !Array.isArray(exercise.placeholders) ||
    exercise.placeholders.length === 0
  ) {
    console.warn("No placeholders defined for this exercise");
    const noPlaceholders = document.createElement("div");
    noPlaceholders.className = "alert alert-info";
    noPlaceholders.textContent =
      "No input parameters required for this exercise.";
    placeholderFields.appendChild(noPlaceholders);
    return;
  }

  // Create input fields for each placeholder
  exercise.placeholders.forEach((placeholder) => {
    if (!placeholder || typeof placeholder !== "object" || !placeholder.name) {
      console.warn("Invalid placeholder format:", placeholder);
      return;
    }

    const formGroup = document.createElement("div");
    formGroup.className = "form-group mb-3";

    // Create label
    const label = document.createElement("label");
    label.setAttribute("for", `placeholder-${placeholder.name}`);
    label.textContent = placeholder.name;
    if (placeholder.type === "regex" && placeholder.regex_pattern) {
      label.textContent += ` (regex: ${placeholder.regex_pattern})`;
    } else if (placeholder.type) {
      label.textContent += ` (${placeholder.type})`;
    }
    formGroup.appendChild(label);

    // Create input
    const input = document.createElement("input");
    input.className = "form-control";
    input.id = `placeholder-${placeholder.name}`;
    input.setAttribute("data-name", placeholder.name);
    input.setAttribute("data-type", placeholder.type || "str");
    if (placeholder.type === "regex" && placeholder.regex_pattern) {
      input.setAttribute("data-pattern", placeholder.regex_pattern);
    }
    // Set default value if available
    if (placeholder.default_value) {
      input.value = placeholder.default_value;
    }
    formGroup.appendChild(input);

    // Error message container
    const errorDiv = document.createElement("div");
    errorDiv.className = "input-error";
    errorDiv.id = `error-${placeholder.name}`;
    errorDiv.style.display = "none";
    formGroup.appendChild(errorDiv);

    placeholderFields.appendChild(formGroup);

    // Add validation listener
    input.addEventListener("input", () => validatePlaceholderInput(input));
  });

  // Add form submit handler
  const form = document.getElementById("placeholder-form");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    executeQuery();
  });

  // Add reset handler
  form.addEventListener("reset", function (e) {
    // Clear stored inputs for this exercise
    let storedInputs = JSON.parse(
      localStorage.getItem("exercise_inputs") || "{}",
    );
    if (storedInputs[exercise.id]) {
      delete storedInputs[exercise.id];
      localStorage.setItem("exercise_inputs", JSON.stringify(storedInputs));
    }

    // Give time for the form to reset, then restore default values
    setTimeout(() => {
      // Restore default values if available
      if (Array.isArray(exercise.placeholders)) {
        exercise.placeholders.forEach((placeholder) => {
          if (placeholder.default_value) {
            const input = document.getElementById(`placeholder-${placeholder.name}`);
            if (input) {
              input.value = placeholder.default_value;
            }
          }
        });
      }
      
      updateEditorWithPlaceholders();
    }, 50);
  });

  // Load any previously saved inputs
  loadInputsFromSession();
  
  // Validate all inputs after setup to update the editor with default values
  exercise.placeholders.forEach((placeholder) => {
    const input = document.getElementById(`placeholder-${placeholder.name}`);
    if (input) {
      validatePlaceholderInput(input);
    }
  });

  // Show solution if available (this might be a previously solved exercise)
  const storedSolutions = JSON.parse(
    localStorage.getItem("exercise_solutions") || "{}",
  );
  const solution = storedSolutions[exercise.id];

  if (solution && isSolved) {
    // Add a solution banner that can be clicked to restore the solution
    const solutionBanner = document.createElement("div");
    solutionBanner.className =
      "alert alert-success mt-3 d-flex justify-content-between align-items-center";
    solutionBanner.innerHTML = `
            <div>
                <strong>You've solved this before!</strong>
                <span class="small text-muted ms-2">
                    (${new Date(solution.solvedAt).toLocaleString()})
                </span>
            </div>
            <button class="btn btn-sm btn-outline-success" id="load-solution-btn">
                Load Solution
            </button>
        `;
    form.appendChild(solutionBanner);

    // Add handler to load the solution
    document
      .getElementById("load-solution-btn")
      .addEventListener("click", function () {
        // Populate inputs with the solution
        Object.keys(solution.inputs).forEach((name) => {
          const input = document.getElementById(`placeholder-${name}`);
          if (input) {
            input.value = solution.inputs[name];
            validatePlaceholderInput(input);
          }
        });

        // Update the editor
        updateEditorWithPlaceholders();
      });
  }
}

/**
 * Validate placeholder input based on its type
 */
function validatePlaceholderInput(input) {
  const name = input.getAttribute("data-name");
  const type = input.getAttribute("data-type");
  const value = input.value.trim();
  const errorDiv = document.getElementById(`error-${name}`);

  let isValid = true;
  let errorMessage = "";

  // Validate based on type
  if (type === "int") {
    isValid = /^-?\d+$/.test(value);
    errorMessage = "Please enter a valid integer";
  } else if (type === "regex") {
    const pattern = input.getAttribute("data-pattern");
    const regex = new RegExp(pattern);
    isValid = regex.test(value);
    errorMessage = `Input must match pattern: ${pattern}`;
  }

  // Update UI
  if (!isValid && value !== "") {
    input.classList.add("is-invalid");
    errorDiv.textContent = errorMessage;
    errorDiv.style.display = "block";
  } else {
    input.classList.remove("is-invalid");
    errorDiv.style.display = "none";
  }

  // Update editor with current values
  updateEditorWithPlaceholders();

  return isValid;
}

/**
 * Update the editor with the current placeholder values
 */
function updateEditorWithPlaceholders() {
  if (!editor || typeof exercise === "undefined") return;

  let query = exercise.base_query;

  // Replace placeholders with input values
  exercise.placeholders.forEach((placeholder) => {
    const input = document.getElementById(`placeholder-${placeholder.name}`);
    if (input) {
      const value = input.value.trim();
      query = query.replace(
        `:${placeholder.name}`,
        value || `:${placeholder.name}`,
      );
    }
  });

  // Update editor
  editor.setValue(query);
}

/**
 * Execute the SQL query with the placeholder values
 */
function executeQuery() {
  if (!db || typeof exercise === "undefined") return;

  // Clear previous results
  hideResults();
  
  // Track view count for this exercise in this session
  trackExerciseView(exercise.id);

  // Get the query with placeholders replaced
  let query = exercise.base_query;
  let allInputsValid = true;
  let allInputsFilled = true;

  // Store input values
  const inputValues = {};

  // Replace placeholders with input values
  if (Array.isArray(exercise.placeholders)) {
    exercise.placeholders.forEach((placeholder) => {
      if (!placeholder || !placeholder.name) return;

      const input = document.getElementById(`placeholder-${placeholder.name}`);
      if (input) {
        let value = input.value.trim();

        // Store value for session storage
        inputValues[placeholder.name] = value;

        // Check if input is filled
        if (!value) {
          allInputsFilled = false;
          input.classList.add("is-invalid");
          const errorDiv = document.getElementById(`error-${placeholder.name}`);
          if (errorDiv) {
            errorDiv.textContent = "This field is required";
            errorDiv.style.display = "block";
          }
        }

        // Check if input is valid
        if (!validatePlaceholderInput(input)) {
          allInputsValid = false;
        }

        // Apply sanitization if available
        if (
          window.paramSanitizers &&
          window.paramSanitizers[placeholder.name]
        ) {
          try {
            // Apply the sanitizer function to the value
            value = window.paramSanitizers[placeholder.name](value);
            // Store the sanitized value for display
            input.setAttribute("data-sanitized-value", value);

            if (exercise.show_query) {
              console.log(`Sanitized ${placeholder.name}: ${value}`);
            }
          } catch (error) {
            console.error(
              `Error in sanitization for ${placeholder.name}:`,
              error,
            );
          }
        }

        // Replace placeholder with value
        query = query.replace(`:${placeholder.name}`, value);
      }
    });
  }

  // Save input values to session storage
  saveInputsToSession(inputValues);

  // If inputs are not valid or filled, don't execute query
  if (!allInputsValid || !allInputsFilled) {
    return;
  }

  // Log query if show_query is enabled, otherwise log sanitized message
  if (exercise.show_query) {
    console.log("Executing query:", query);
  } else {
    console.log("Executing query (hidden)");
  }

  // Show loading indicator
  showLoading();
  
  // Disable the run button during execution
  const runJsButton = document.getElementById("run-js-btn");
  if (runJsButton) {
    runJsButton.disabled = true;
  }

  // Use setTimeout to allow the loading indicator to render
  setTimeout(() => {
    try {
      // Execute the query
      const result = db.exec(query);

      // Check for flag in the results
      const flagFound = checkForFlag(result);

      // Add a small delay for better UX
      setTimeout(() => {
        // Hide loading indicator
        hideLoading();

        // Display results
        displayResults(result);

        // Show success message if flag found
        if (flagFound) {
          // Mark as solved in session if not already solved 
          if (!isSolved) {
            markExerciseSolved(inputValues)
              .then(responseData => {
                // Show success with stats
                showSuccess(responseData ? responseData.stats : null);
              });
          } else {
            showSuccess();
          }

          // Add confetti effect on success
          if (typeof confetti !== "undefined") {
            confetti({
              particleCount: 100,
              spread: 70,
              origin: { y: 0.6 },
            });
          }
        }
      }, 300);
    } catch (error) {
      console.error("Query execution error:", error);

      // Hide loading indicator
      hideLoading();

      // Show error message if enabled for this exercise
      if (exercise.show_errors) {
        // If we don't show the query, make sure we don't leak query details in error messages
        if (exercise.show_query) {
          showError(error.message);
        } else {
          // Filter error message to avoid revealing query structure
          let filteredMessage = error.message;

          // Remove SQL syntax that might reveal the query structure
          filteredMessage = filteredMessage.replace(
            /near "([^"]+)"/,
            'near "..."',
          );
          filteredMessage = filteredMessage.replace(
            /at offset \d+/,
            "at offset ...",
          );

          showError(filteredMessage);
        }
      } else {
        // Show generic error if errors are disabled
        showError("Query execution failed. Try a different approach.");
      }
    }
  }, 100);
}

/**
 * Check if the flag appears in the query results and anti-flag does not
 */
function checkForFlag(results) {
  if (!results || results.length === 0 || !exercise.expected_flag) return false;

  // Convert flag to lowercase for case-insensitive comparison
  const expectedFlag = exercise.expected_flag.toLowerCase();

  // Convert anti-flag to lowercase if it exists
  const antiFlag = exercise.anti_flag ? exercise.anti_flag.toLowerCase() : null;

  // First check if anti-flag appears in results - if it does, fail
  if (antiFlag) {
    for (const result of results) {
      if (!result.values) continue;

      for (const row of result.values) {
        for (const cell of row) {
          // Check if the cell contains the anti-flag (case-insensitive)
          if (cell && cell.toString().toLowerCase().includes(antiFlag)) {
            console.log("Anti-flag found in results - challenge not solved");
            return false;
          }
        }
      }
    }
  }

  // Check each result for the flag
  for (const result of results) {
    if (!result.values) continue;

    for (const row of result.values) {
      for (const cell of row) {
        // Check if the cell contains the flag (case-insensitive)
        if (cell && cell.toString().toLowerCase().includes(expectedFlag)) {
          return true;
        }
      }
    }
  }

  return false;
}

/**
 * Display query results in the table
 */
function displayResults(results) {
  const resultsContainer = document.getElementById("results-container");
  const resultsTable = document.getElementById("results-table");

  // Update the results header based on show_query setting
  const resultsHeader = resultsContainer.querySelector("h5");
  if (resultsHeader) {
    resultsHeader.textContent = exercise.show_query
      ? "Query Results"
      : "Results";
  }

  // Clear previous results
  resultsTable.innerHTML = "";

  if (!results || results.length === 0) {
    // No results
    resultsTable.innerHTML = "<tr><td>No results returned</td></tr>";
  } else {
    // Process and display each result set
    results.forEach((result) => {
      if (!result.columns || !result.values) return;

      // Create table header
      const thead = document.createElement("thead");
      const headerRow = document.createElement("tr");

      result.columns.forEach((column, i) => {
        const th = document.createElement("th");
        if (exercise.show_query) {
          th.textContent = column;
        } else {
          th.textContent = i;
        }

        headerRow.appendChild(th);
      });

      thead.appendChild(headerRow);
      resultsTable.appendChild(thead);

      // Create table body
      const tbody = document.createElement("tbody");

      result.values.forEach((row) => {
        const tr = document.createElement("tr");

        row.forEach((cell) => {
          const td = document.createElement("td");
          td.textContent = cell !== null ? cell : "NULL";
          tr.appendChild(td);
        });

        tbody.appendChild(tr);
      });

      resultsTable.appendChild(tbody);
    });
  }

  // Show results container
  resultsContainer.style.display = "block";
}

/**
 * Show error message
 */
function showError(message) {
  const errorContainer = document.getElementById("error-container");
  const errorMessage = document.getElementById("error-message");

  // Update error header based on show_query setting
  const errorHeader = errorContainer.querySelector("h5");
  if (errorHeader) {
    errorHeader.textContent = exercise.show_query ? "SQL Error" : "Error";
  }

  errorMessage.textContent = message;
  errorContainer.style.display = "block";
}

/**
 * Show success message
 */
function showSuccess(statsData) {
  const successContainer = document.getElementById("success-container");
  successContainer.style.display = "block";
  
  // If we have stats data, display it
  if (statsData && successContainer.querySelector(".success-stats")) {
    const statsElement = successContainer.querySelector(".success-stats");
    statsElement.innerHTML = `
      <div class="mt-2">
        <small class="text-muted">
          This challenge has been viewed ${statsData.views} times and solved ${statsData.solves} times.
        </small>
      </div>
    `;
  }

  // Update UI to show the exercise is solved
  isSolved = true;
}

/**
 * Hide all result containers
 */
function hideResults() {
  document.getElementById("results-container").style.display = "none";
  document.getElementById("error-container").style.display = "none";
  document.getElementById("success-container").style.display = "none";
}

/**
 * Show loading indicator
 */
function showLoading() {
  // Create loading container if it doesn't exist
  let loadingContainer = document.getElementById("loading-container");

  if (!loadingContainer) {
    loadingContainer = document.createElement("div");
    loadingContainer.id = "loading-container";
    loadingContainer.className = "text-center my-4";

    const loadingElement = document.createElement("div");
    loadingElement.className = "loading";

    const loadingText = document.createElement("p");
    loadingText.textContent = "Executing query...";
    loadingText.className = "mt-2 text-muted";

    loadingContainer.appendChild(loadingElement);
    loadingContainer.appendChild(loadingText);

    // Insert after the placeholder form or js editor section
    const placeholderForm = document.getElementById("placeholder-form");
    if (placeholderForm) {
      placeholderForm.parentNode.insertBefore(
        loadingContainer,
        placeholderForm.nextSibling,
      );
    } else {
      // For JS mode, insert after the js-editor-section
      const jsEditorSection = document.getElementById("js-editor-section");
      if (jsEditorSection) {
        jsEditorSection.parentNode.insertBefore(
          loadingContainer,
          jsEditorSection.nextSibling,
        );
      } else {
        // Fallback to appending to the sql-editor-section
        document.getElementById("sql-editor-section").appendChild(loadingContainer);
      }
    }
  }

  loadingContainer.style.display = "block";

  // Disable form inputs and button during loading
  const submitButton = document.querySelector(
    '#placeholder-form button[type="submit"]',
  );
  if (submitButton) {
    submitButton.disabled = true;
  }

  const inputs = document.querySelectorAll("#placeholder-form input");
  inputs.forEach((input) => {
    input.disabled = true;
  });
}

/**
 * Hide loading indicator
 */
function hideLoading() {
  const loadingContainer = document.getElementById("loading-container");
  if (loadingContainer) {
    loadingContainer.style.display = "none";
  }

  // Re-enable form inputs and button if in placeholder mode
  const placeholderForm = document.getElementById("placeholder-form");
  if (placeholderForm) {
    const submitButton = document.querySelector(
      '#placeholder-form button[type="submit"]',
    );
    if (submitButton) {
      submitButton.disabled = false;
    }

    const inputs = document.querySelectorAll("#placeholder-form input");
    inputs.forEach((input) => {
      input.disabled = false;
    });
  } else if (exercise.allow_js) {
    // Re-enable JS run button if in JS mode
    const runJsButton = document.getElementById("run-js-btn");
    if (runJsButton) {
      runJsButton.disabled = false;
    }
  }
}

/**
 * Save input values to session storage
 */
function saveInputsToSession(inputValues) {
  // Get existing stored inputs or initialize empty object
  let storedInputs = JSON.parse(
    localStorage.getItem("exercise_inputs") || "{}",
  );

  // Store inputs for this exercise
  storedInputs[exercise.id] = inputValues;

  // Save back to localStorage
  localStorage.setItem("exercise_inputs", JSON.stringify(storedInputs));
}

/**
 * Load input values from session storage
 */
function loadInputsFromSession() {
  // Get stored inputs
  const storedInputs = JSON.parse(
    localStorage.getItem("exercise_inputs") || "{}",
  );

  // Check if we have stored inputs for this exercise
  const exerciseInputs = storedInputs[exercise.id];
  if (exerciseInputs) {
    // Populate form fields with stored values
    Object.keys(exerciseInputs).forEach((name) => {
      const input = document.getElementById(`placeholder-${name}`);
      if (input) {
        // Only set value if there's a stored value (non-empty string)
        if (exerciseInputs[name] !== '') {
          input.value = exerciseInputs[name];
          // Validate the input
          validatePlaceholderInput(input);
        }
      }
    });

    // Update the editor with the loaded values
    updateEditorWithPlaceholders();
  }
}

/**
 * Mark exercise as solved in the session
 * @returns {Promise} Promise that resolves with the server response data
 */
/**
 * Track that an exercise was viewed in this session and increment server counter
 */
function trackExerciseView(exerciseId) {
  // Initialize viewed_exercises in session if not exists
  let viewedExercises = JSON.parse(
    sessionStorage.getItem("viewed_exercises") || "[]"
  );
  
  // Only track the first view per session
  if (!viewedExercises.includes(exerciseId)) {
    // Add to viewed exercises
    viewedExercises.push(exerciseId);
    sessionStorage.setItem("viewed_exercises", JSON.stringify(viewedExercises));
    
    // Get CSRF token
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
      console.error("CSRF token not found - cannot track exercise view");
      return;
    }
    
    // Send to the server
    fetch(`/exercise/${exerciseId}/viewed/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      }
    }).catch(error => {
      console.error("Error tracking exercise view:", error);
    });
  }
}

/**
 * Mark exercise as solved in the session
 * @returns {Promise} Promise that resolves with the server response data
 */
function markExerciseSolved(inputValues) {
  console.warn("marking as solved");
  // Store the solution inputs with a success flag
  let storedSolutions = JSON.parse(
    localStorage.getItem("exercise_solutions") || "{}",
  );
  storedSolutions[exercise.id] = {
    inputs: inputValues,
    solvedAt: new Date().toISOString(),
  };
  localStorage.setItem("exercise_solutions", JSON.stringify(storedSolutions));

  // Get CSRF token
  const csrfToken = getCsrfToken();
  if (!csrfToken) {
    console.error(
      "CSRF token not found - cannot mark exercise as solved on server",
    );
    return Promise.resolve(null);
  }

  // Update isSolved state
  isSolved = true;

  // Log the data we're sending
  const requestData = {
    exerciseId: exercise.id,
    solution: inputValues,
  };
  console.log("Sending solution data:", requestData);

  // Send to the server
  return fetch(`/exercise/${exercise.id}/solved/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(requestData),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Server responded with status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Exercise marked as solved on server:", data);
      return data;
    })
    .catch((error) => {
      console.error("Error marking exercise as solved:", error);

      // Even if server fails, we still consider it solved locally
      isSolved = true;
      return null;
    });
}

/**
 * Set up the JavaScript editor for advanced exercises
 */
function setupJsEditor() {
  if (typeof exercise === "undefined" || !exercise.allow_js) return;

  const jsEditorElement = document.getElementById("js-editor");
  if (!jsEditorElement) return;

  // Create a JavaScript template with helpful comments, examples, and parameter info
  let placeholdersInfo = "";
  if (
    Array.isArray(exercise.placeholders) &&
    exercise.placeholders.length > 0
  ) {
    placeholdersInfo =
      "// IMPORTANT: Available parameters for this exercise:\n";
    exercise.placeholders.forEach((p) => {
      placeholdersInfo += `// - ${p.name}: ${p.type || "string"}${p.regex_pattern ? ` (pattern: ${p.regex_pattern})` : ""}${p.default_value ? ` (default: ${p.default_value})` : ""}\n`;
    });
    placeholdersInfo += "//\n";
  } else {
    placeholdersInfo =
      "// NOTE: This exercise has no defined placeholders.\n//\n";
  }

  // Generate examples based on available placeholders
  let examples = "";
  if (
    Array.isArray(exercise.placeholders) &&
    exercise.placeholders.length > 0
  ) {
    // Create examples for both calling styles
    const placeholderNames = exercise.placeholders.map((p) => p.name);

    // Named parameters style example
    let namedParamsExample =
      "// Using named parameters (object):\n// execQuery({";
    namedParamsExample += placeholderNames
      .map((name) => `${name}: "value"`)
      .join(", ");
    namedParamsExample += "});\n\n";

    // Positional parameters style example
    let positionalParamsExample =
      "// Using positional parameters (same order as listed above):\n// execQuery(";
    positionalParamsExample += placeholderNames.map(() => `"value"`).join(", ");
    positionalParamsExample += ");\n";

    examples = namedParamsExample + positionalParamsExample;
  } else {
    examples = "// No parameters needed for this exercise:\n// execQuery();\n";
  }

  const jsTemplate = `// Use execQuery function to run the predefined query with your parameter values
// The base query is: ${exercise.base_query.replace(/\n/g, " ").replace(/"/g, '\\"')}
//
// You don't need to provide the SQL query - only the values for placeholders
// Returns: Array of result objects from SQL.js

${placeholdersInfo}
// Examples:
${examples}

// For time-based/blind injection challenges:
// Use async/await with setTimeout to measure time differences

async function runExploit() {
  // Your exploit code here
  // For example, to extract a password character by character:

  let extractedData = '';
  const possibleChars = 'abcdefghijklmnopqrstuvwxyz0123456789_-{}!@#$%^&*()';

  for (let position = 1; position <= 8; position++) {
    for (let i = 0; i < possibleChars.length; i++) {
      const char = possibleChars[i];
      const startTime = performance.now();

      const result = execQuery(
        'SELECT * FROM users WHERE username = "admin" AND substr(password, ' + position + ', 1) = "' + char + '" AND 1=sleep(0.1)'
      );

      const endTime = performance.now();
      const timeDiff = endTime - startTime;

      if (timeDiff > 100) {  // If query took longer than 100ms
        extractedData += char;
        console.log('Found character at position ' + position + ': ' + char);
        break;
      }
    }
  }

  console.log('Extracted data: ' + extractedData);
}

// Call your exploit function
runExploit();
`;

  // Initialize CodeMirror
  jsEditor = CodeMirror(jsEditorElement, {
    value: jsTemplate,
    mode: "javascript",
    theme: "dracula",
    lineNumbers: true,
    matchBrackets: true,
    autoCloseBrackets: true,
    indentUnit: 2,
  });

  // Add console output div if it doesn't exist
  let consoleOutput = document.getElementById("js-console-output");
  if (!consoleOutput) {
    consoleOutput = document.createElement("div");
    consoleOutput.id = "js-console-output";
    consoleOutput.className = "js-console-output";
    consoleOutput.style.display = "none";

    // Insert after the JS editor section
    const jsEditorSection = document.getElementById("js-editor-section");
    jsEditorSection.parentNode.insertBefore(
      consoleOutput,
      jsEditorSection.nextSibling,
    );
  }

  // Override console.log for the JavaScript evaluation
  const originalConsoleLog = console.log;
  const originalConsoleError = console.error;
  const originalConsoleWarn = console.warn;

  // Run button event handler
  const runJsButton = document.getElementById("run-js-btn");
  if (runJsButton) {
    runJsButton.addEventListener("click", function () {
      // Clear previous results
      hideResults();

      // Clear console output
      consoleOutput.innerHTML = "";
      consoleOutput.style.display = "block";

      // Override console methods to capture output
      console.log = function () {
        const args = Array.from(arguments);
        originalConsoleLog.apply(console, args);
        const logLine = document.createElement("div");
        logLine.className = "log";
        logLine.textContent = args
          .map((arg) =>
            typeof arg === "object" ? JSON.stringify(arg, null, 2) : arg,
          )
          .join(" ");
        consoleOutput.appendChild(logLine);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
      };

      console.error = function () {
        const args = Array.from(arguments);
        originalConsoleError.apply(console, args);
        const errorLine = document.createElement("div");
        errorLine.className = "error";
        errorLine.textContent = args
          .map((arg) =>
            typeof arg === "object" ? JSON.stringify(arg, null, 2) : arg,
          )
          .join(" ");
        consoleOutput.appendChild(errorLine);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
      };

      console.warn = function () {
        const args = Array.from(arguments);
        originalConsoleWarn.apply(console, args);
        const warnLine = document.createElement("div");
        warnLine.className = "warn";
        warnLine.textContent = args
          .map((arg) =>
            typeof arg === "object" ? JSON.stringify(arg, null, 2) : arg,
          )
          .join(" ");
        consoleOutput.appendChild(warnLine);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
      };

      try {
        // Show loading indicator
        showLoading();

        // Execute the JavaScript code
        const jsCode = jsEditor.getValue();

        // Define the execQuery function that directly accepts placeholder values as parameters
        // without requiring the user to specify the query string
        window.execQuery = function (...args) {
          if (!db) {
            console.error("Database not initialized");
            return null;
          }

          try {
            // Start with the base query from the exercise
            let processedQuery = exercise.base_query;
            let params = {};

            // Get the list of valid placeholders from the exercise
            const validPlaceholders = Array.isArray(exercise.placeholders)
              ? exercise.placeholders.map((p) => p.name)
              : [];

            // Handle different function call formats
            if (
              args.length === 1 &&
              typeof args[0] === "object" &&
              args[0] !== null
            ) {
              // Called with an object of parameters: execQuery({param1: 'value1', param2: 'value2'})
              params = args[0];
            } else if (validPlaceholders.length === args.length) {
              // Called with sequential parameters: execQuery('value1', 'value2')
              params = {};
              validPlaceholders.forEach((name, index) => {
                params[name] = args[index];
              });
            } else {
              // Incorrect parameter count
              throw new Error(
                `Expected ${validPlaceholders.length} parameters (${validPlaceholders.join(", ")}), but got ${args.length}`,
              );
            }

            // Validate parameters against the defined placeholders
            if (Object.keys(params).length > 0) {
              // Check for invalid parameters
              const invalidParams = Object.keys(params).filter(
                (key) => !validPlaceholders.includes(key),
              );
              if (invalidParams.length > 0) {
                console.error(
                  `Invalid parameters provided: ${invalidParams.join(", ")}`,
                );
                console.error(
                  `Valid parameters are: ${validPlaceholders.join(", ")}`,
                );
                throw new Error(
                  `Invalid parameters provided. Only the following parameters are allowed: ${validPlaceholders.join(", ")}`,
                );
              }

              // Apply any available sanitizers
              for (const [key, value] of Object.entries(params)) {
                // Apply sanitization if available
                if (window.paramSanitizers && window.paramSanitizers[key]) {
                  try {
                    // Apply the sanitizer function to the value
                    params[key] = window.paramSanitizers[key](value);

                    if (exercise.show_query) {
                      console.log(`Sanitized ${key}: ${params[key]}`);
                    }
                  } catch (error) {
                    console.error(`Error in sanitization for ${key}:`, error);
                  }
                }
              }

              // Replace parameters in the query
              for (const [key, value] of Object.entries(params)) {
                // Create a regex pattern to find the placeholder (e.g., :name)
                const pattern = new RegExp(`:${key}\\b`, "g");
                // Replace the placeholder with the value
                processedQuery = processedQuery.replace(pattern, value);
              }
            }

            // Log query if show_query is enabled
            if (exercise.show_query) {
              console.log("Executing query:", processedQuery);
            } else {
              console.log("Executing query (hidden)");
            }

            // Execute the query
            const result = db.exec(processedQuery);

            // Check for the flag (and anti-flag)
            const flagFound = checkForFlag(result);
            if (flagFound && !isSolved) {
              // Check the anti-flag separately (for detailed logging)
              if (exercise.anti_flag) {
                const antiFlag = exercise.anti_flag.toLowerCase();
                let antiFlagFound = false;

                // Check if any result contains the anti-flag
                for (const res of result) {
                  if (!res.values) continue;
                  for (const row of res.values) {
                    for (const cell of row) {
                      if (
                        cell &&
                        cell.toString().toLowerCase().includes(antiFlag)
                      ) {
                        antiFlagFound = true;
                        break;
                      }
                    }
                    if (antiFlagFound) break;
                  }
                  if (antiFlagFound) break;
                }

                if (antiFlagFound) {
                  console.log(
                    "Flag found but anti-flag also found. Challenge not solved.",
                  );
                  return result;
                }
              }

              console.log("SUCCESS! Flag found:", exercise.expected_flag);
              // Mark as solved
              markExerciseSolved({});
              // Update UI to show success
              showSuccess();

              // Add confetti effect
              if (typeof confetti !== "undefined") {
                confetti({
                  particleCount: 100,
                  spread: 70,
                  origin: { y: 0.6 },
                });
              }
            }

            // Return the result
            return result;
          } catch (error) {
            // Handle errors according to show_errors setting
            if (exercise.show_errors) {
              if (exercise.show_query) {
                console.error("SQL Error:", error.message);
              } else {
                // Filter error message to avoid revealing query structure
                let filteredMessage = error.message;
                filteredMessage = filteredMessage.replace(
                  /near "([^"]+)"/,
                  'near "..."',
                );
                filteredMessage = filteredMessage.replace(
                  /at offset \d+/,
                  "at offset ...",
                );
                console.error("Error:", filteredMessage);
              }
            } else {
              console.error("Query execution failed. Try a different approach.");
            }
            return null;
          }
      };

        // Define a sleep function for time-based techniques
        window.sleep = function (ms) {
          return new Promise((resolve) => setTimeout(resolve, ms));
        };

        // Execute the code
        new Function(jsCode)();
      } catch (error) {
        console.error("JavaScript execution error:", error.message);
      } finally {
        // Hide loading indicator
        hideLoading();

        // Restore original console methods
        console.log = originalConsoleLog;
        console.error = originalConsoleError;
        console.warn = originalConsoleWarn;
      }
  });
  
  // Reset button event handler
  const resetJsButton = document.getElementById("reset-js-btn");
  if (resetJsButton) {
    resetJsButton.addEventListener("click", function () {
      jsEditor.setValue(jsTemplate);
      consoleOutput.innerHTML = "";
      consoleOutput.style.display = "none";
      hideResults();
    });
  }
}
} // End of setupJsEditor function

/**
 * Get CSRF token from meta tag or cookie
 */
function getCsrfToken() {
  // First check if we have a CSRF token in the DOM
  const tokenElement = document.querySelector("[name=csrfmiddlewaretoken]");
  if (tokenElement) {
    return tokenElement.value;
  }

  // Fall back to cookie-based lookup
  const name = "csrftoken";
  let cookieValue = null;

  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }

  // Debug output to help diagnose CSRF issues
  console.log("CSRF Token:", cookieValue || "Not found");

  return cookieValue;
}
