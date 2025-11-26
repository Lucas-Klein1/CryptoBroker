console.log("CryptoSim frontend loaded");
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".portfolio-row, .dashboard-row, .transaction-row")
        .forEach(row => {
            row.addEventListener("click", () => {
                const target = row.dataset.href;
                if (target) window.location = target;
            });
        });
});


