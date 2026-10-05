
"use strict";

// =====================================================
// AI BUSINESS INTELLIGENCE - DASHBOARD JAVASCRIPT
// =====================================================

// Chart variables
let monthlyChart = null;
let categoryChart = null;
let regionChart = null;
let forecastChart = null;

// =====================================================
// HELPER FUNCTIONS
// =====================================================

function formatCurrency(value) {
    const number = Number(value) || 0;

    return number.toLocaleString("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0
    });
}

function formatNumber(value) {
    return (Number(value) || 0).toLocaleString("en-IN");
}

function getElement(id) {
    const element = document.getElementById(id);

    if (!element) {
        console.warn("HTML element not found:", id);
    }

    return element;
}

function setText(id, value) {
    const element = getElement(id);

    if (element) {
        element.textContent =
            value === null || value === undefined
                ? "-"
                : String(value);
    }
}

async function fetchJSON(url) {
    const response = await fetch(url, {
        cache: "no-store"
    });

    if (!response.ok) {
        throw new Error(
            "Request failed: " + url + " (" + response.status + ")"
        );
    }

    return await response.json();
}

function getArray(data) {
    if (Array.isArray(data)) {
        return data;
    }

    if (data && Array.isArray(data.data)) {
        return data.data;
    }

    if (data && Array.isArray(data.results)) {
        return data.results;
    }

    if (data && Array.isArray(data.forecast)) {
        return data.forecast;
    }

    return [];
}

function getValue(row, keys, fallback) {
    if (!row) {
        return fallback;
    }

    for (let i = 0; i < keys.length; i++) {
        const key = keys[i];

        if (
            row[key] !== undefined &&
            row[key] !== null
        ) {
            return row[key];
        }
    }

    return fallback;
}

function createQueryString() {
    const params = new URLSearchParams();

    const category = getElement("categoryFilter");
    const region = getElement("regionFilter");
    const month = getElement("monthFilter");

    if (
        category &&
        category.value &&
        category.value !== "All"
    ) {
        params.set("category", category.value);
    }

    if (
        region &&
        region.value &&
        region.value !== "All"
    ) {
        params.set("region", region.value);
    }

    if (
        month &&
        month.value &&
        month.value !== "All"
    ) {
        params.set("month", month.value);
    }

    const query = params.toString();

    return query ? "?" + query : "";
}

// =====================================================
// PAGE INITIALIZATION
// =====================================================

document.addEventListener("DOMContentLoaded", function () {
    console.log("Dashboard JavaScript loaded.");

    if (typeof Chart === "undefined") {
        console.error(
            "Chart.js is not loaded. Check the Chart.js script in index.html."
        );
    } else {
        console.log("Chart.js version:", Chart.version);
    }

    setupFilters();
    initializeDashboard();
});

async function initializeDashboard() {
    try {
        await loadFilterOptions();
    } catch (error) {
        console.error("Could not load filter options:", error);
    }

    await loadDashboard();
}

// =====================================================
// FILTER OPTIONS
// =====================================================

async function loadFilterOptions() {
    const data = await fetchJSON("/api/filter-options");

    console.log("Filter Options:", data);

    fillDropdown(
        "categoryFilter",
        data.categories || [],
        "All Categories"
    );

    fillDropdown(
        "regionFilter",
        data.regions || [],
        "All Regions"
    );

    fillDropdown(
        "monthFilter",
        data.months || [],
        "All Months"
    );
}

function fillDropdown(id, values, defaultLabel) {
    const select = getElement(id);

    if (!select) {
        return;
    }

    const previousValue = select.value;

    select.innerHTML = "";

    const defaultOption = document.createElement("option");
    defaultOption.value = "All";
    defaultOption.textContent = defaultLabel;
    select.appendChild(defaultOption);

    values.forEach(function (value) {
        const option = document.createElement("option");
        option.value = String(value);
        option.textContent = String(value);
        select.appendChild(option);
    });

    const stillExists = Array.from(select.options).some(
        function (option) {
            return option.value === previousValue;
        }
    );

    select.value = stillExists ? previousValue : "All";
}

// =====================================================
// FILTER EVENT LISTENERS
// =====================================================

function setupFilters() {
    const category = getElement("categoryFilter");
    const region = getElement("regionFilter");
    const month = getElement("monthFilter");
    const resetButton = getElement("resetFilters");
    const refreshButton = getElement("refreshButton");

    if (category) {
        category.addEventListener("change", loadDashboard);
    }

    if (region) {
        region.addEventListener("change", loadDashboard);
    }

    if (month) {
        month.addEventListener("change", loadDashboard);
    }

    if (resetButton) {
        resetButton.addEventListener("click", resetFilters);
    }

    if (refreshButton) {
        refreshButton.addEventListener("click", refreshDashboard);
    }
}

function resetFilters() {
    const category = getElement("categoryFilter");
    const region = getElement("regionFilter");
    const month = getElement("monthFilter");

    if (category) category.value = "All";
    if (region) region.value = "All";
    if (month) month.value = "All";

    loadDashboard();
}

async function refreshDashboard() {
    try {
        await loadFilterOptions();
    } catch (error) {
        console.error("Filter refresh failed:", error);
    }

    await loadDashboard();
}

// =====================================================
// LOAD ALL DASHBOARD SECTIONS
// =====================================================

async function loadDashboard() {
    const query = createQueryString();

    console.log("Loading dashboard. Active query:", query);

    // Load each section independently so one failure
    // does not prevent the remaining sections from loading.
    const tasks = [
        loadKPIs(query),
        loadMonthlySales(query),
        loadCategorySales(query),
        loadRegionSales(query),
        loadSalesTable(query),
        loadForecast(),
        loadForecastInsights()
    ];

    const results = await Promise.allSettled(tasks);

    results.forEach(function (result, index) {
        if (result.status === "rejected") {
            console.error(
                "Dashboard section " + (index + 1) + " failed:",
                result.reason
            );
        }
    });
}

// =====================================================
// KPI CARDS
// =====================================================

async function loadKPIs(query) {
    const data = await fetchJSON("/api/kpis" + query);

    console.log("KPI Response:", data);

    setText(
        "totalSales",
        formatCurrency(
            getValue(data, ["total_sales", "Total_Sales"], 0)
        )
    );

    setText(
        "totalOrders",
        formatNumber(
            getValue(data, ["total_orders", "Total_Orders"], 0)
        )
    );

    setText(
        "totalCustomers",
        formatNumber(
            getValue(
                data,
                ["total_customers", "unique_customers", "Customers"],
                0
            )
        )
    );

    setText(
        "averageOrderValue",
        formatCurrency(
            getValue(
                data,
                ["average_order_value", "avg_order_value"],
                0
            )
        )
    );
}

// =====================================================
// MONTHLY SALES CHART
// =====================================================

async function loadMonthlySales(query) {
    const result = await fetchJSON("/api/monthly-sales" + query);
    const rows = getArray(result);

    console.log("Monthly Sales:", result);

    const labels = [];
    const values = [];

    rows.forEach(function (row) {
        labels.push(
            getValue(row, ["Month", "month", "Order_Month"], "")
        );

        values.push(
            Number(
                getValue(
                    row,
                    ["Total_Sales", "total_sales", "sales"],
                    0
                )
            ) || 0
        );
    });

    renderMonthlyChart(labels, values);
}

function renderMonthlyChart(labels, values) {
    if (typeof Chart === "undefined") return;

    const canvas = getElement("monthlySalesChart");
    if (!canvas) return;

    if (monthlyChart) {
        monthlyChart.destroy();
    }

    monthlyChart = new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Monthly Sales",
                data: values,
                tension: 0.3,
                fill: false,
                borderWidth: 3,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return formatCurrency(context.raw);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// =====================================================
// CATEGORY SALES CHART
// =====================================================

async function loadCategorySales(query) {
    const result = await fetchJSON("/api/category-sales" + query);
    const rows = getArray(result);

    console.log("Category Sales:", result);

    const labels = [];
    const values = [];

    rows.forEach(function (row) {
        labels.push(
            getValue(row, ["Category", "category"], "Unknown")
        );

        values.push(
            Number(
                getValue(
                    row,
                    ["Total_Sales", "total_sales", "sales"],
                    0
                )
            ) || 0
        );
    });

    renderCategoryChart(labels, values);
}

function renderCategoryChart(labels, values) {
    if (typeof Chart === "undefined") return;

    const canvas = getElement("categorySalesChart");
    if (!canvas) return;

    if (categoryChart) {
        categoryChart.destroy();
    }

    categoryChart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                label: "Category Sales",
                data: values,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom"
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return context.label + ": " +
                                formatCurrency(context.raw);
                        }
                    }
                }
            }
        }
    });
}

// =====================================================
// REGION SALES CHART
// =====================================================

async function loadRegionSales(query) {
    const result = await fetchJSON("/api/region-sales" + query);
    const rows = getArray(result);

    console.log("Region Sales:", result);

    const labels = [];
    const values = [];

    rows.forEach(function (row) {
        labels.push(
            getValue(row, ["Region", "region"], "Unknown")
        );

        values.push(
            Number(
                getValue(
                    row,
                    ["Total_Sales", "total_sales", "sales"],
                    0
                )
            ) || 0
        );
    });

    renderRegionChart(labels, values);
}

function renderRegionChart(labels, values) {
    if (typeof Chart === "undefined") return;

    const canvas = getElement("regionSalesChart");
    if (!canvas) return;

    if (regionChart) {
        regionChart.destroy();
    }

    regionChart = new Chart(canvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Regional Sales",
                data: values,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return formatCurrency(context.raw);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            return formatNumber(value);
                        }
                    }
                }
            }
        }
    });
}

// =====================================================
// SALES TABLE
// =====================================================

async function loadSalesTable(query) {
    const result = await fetchJSON("/api/sales" + query);
    const rows = getArray(result);

    console.log("Sales Table:", result);

    const tableBody = getElement("salesTableBody");
    if (!tableBody) return;

    tableBody.innerHTML = "";

    setText("recordCount", rows.length + " records");

    if (rows.length === 0) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");

        td.colSpan = 8;
        td.textContent = "No sales data found.";

        tr.appendChild(td);
        tableBody.appendChild(tr);
        return;
    }

    rows.forEach(function (row) {
        const tr = document.createElement("tr");

        const cells = [
            getValue(row, ["Order_ID", "order_id"], "-"),
            getValue(row, ["Order_Date", "order_date"], "-"),
            getValue(row, ["Customer_ID", "customer_id"], "-"),
            getValue(row, ["Product", "product"], "-"),
            getValue(row, ["Category", "category"], "-"),
            getValue(row, ["Region", "region"], "-"),
            getValue(row, ["Quantity", "quantity"], 0),
            formatCurrency(
                getValue(row, ["Total_Sales", "total_sales"], 0)
            )
        ];

        cells.forEach(function (value) {
            const td = document.createElement("td");
            td.textContent = String(value);
            tr.appendChild(td);
        });

        tableBody.appendChild(tr);
    });
}

// =====================================================
// AI FORECAST CHART
// =====================================================

async function loadForecast() {
    const result = await fetchJSON("/api/forecast");
    const forecastRows = getArray(result);

    console.log("Forecast:", result);

    if (forecastRows.length === 0) {
        console.warn("No forecast rows returned.");
        return;
    }

    const historicalResult = await fetchJSON("/api/monthly-sales");
    const historicalRows = getArray(historicalResult);

    const historicalLabels = [];
    const historicalValues = [];

    historicalRows.forEach(function (row) {
        historicalLabels.push(
            getValue(row, ["Month", "month"], "")
        );

        historicalValues.push(
            Number(
                getValue(
                    row,
                    ["Total_Sales", "total_sales", "sales"],
                    0
                )
            ) || 0
        );
    });

    const forecastLabels = [];
    const forecastValues = [];

    forecastRows.forEach(function (row) {
        forecastLabels.push(
            getValue(
                row,
                ["month", "Month", "forecast_month"],
                ""
            )
        );

        forecastValues.push(
            Number(
                getValue(
                    row,
                    [
                        "forecasted_sales",
                        "Forecasted_Sales",
                        "sales",
                        "predicted_sales"
                    ],
                    0
                )
            ) || 0
        );
    });

    const allLabels = historicalLabels.concat(forecastLabels);

    const actualData = historicalValues.slice();
    const predictedData = [];

    for (let i = 0; i < historicalValues.length - 1; i++) {
        predictedData.push(null);
    }

    if (historicalValues.length > 0) {
        predictedData.push(
            historicalValues[historicalValues.length - 1]
        );
    }

    forecastValues.forEach(function (value) {
        predictedData.push(value);
    });

    while (actualData.length < allLabels.length) {
        actualData.push(null);
    }

    renderForecastChart(
        allLabels,
        actualData,
        predictedData
    );
}

function renderForecastChart(labels, actual, forecast) {
    if (typeof Chart === "undefined") return;

    const canvas = getElement("forecastChart");
    if (!canvas) return;

    if (forecastChart) {
        forecastChart.destroy();
    }

    forecastChart = new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Actual Sales",
                    data: actual,
                    tension: 0.3,
                    borderWidth: 3,
                    spanGaps: false
                },
                {
                    label: "AI Forecast",
                    data: forecast,
                    tension: 0.3,
                    borderWidth: 3,
                    borderDash: [7, 7],
                    spanGaps: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return context.dataset.label + ": " +
                                formatCurrency(context.raw);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// =====================================================
// FORECAST INSIGHTS
// =====================================================

async function loadForecastInsights() {
    const data = await fetchJSON("/api/forecast-insights");

    console.log("Forecast Insights:", data);

    if (!data || data.status !== "success") {
        console.warn("Forecast insights are unavailable.");
        return;
    }

    const nextMonth = data.next_month || {};
    const highest = data.highest_forecast || {};

    setText(
        "nextMonthForecast",
        formatCurrency(
            getValue(
                nextMonth,
                ["forecasted_sales", "sales"],
                0
            )
        )
    );

    setText(
        "nextForecastMonth",
        getValue(nextMonth, ["month"], "-")
    );

    setText(
        "averageForecast",
        formatCurrency(
            getValue(data, ["average_forecast"], 0)
        )
    );

    setText(
        "highestForecast",
        formatCurrency(
            getValue(highest, ["sales", "forecasted_sales"], 0)
        )
    );

    setText(
        "highestForecastMonth",
        getValue(highest, ["month"], "-")
    );

    const trend = Number(data.overall_change_percentage) || 0;
    const trendText =
        (trend > 0 ? "+" : "") + trend.toFixed(2) + "%";

    setText("overallForecastTrend", trendText);
    setText("forecastInsight", data.insight || "No forecast insight available.");
}

console.log("Dashboard functions ready.");