document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");
    const body = document.body;

    if (!sidebar || !sidebarToggle) {
        return;
    }

    const sidebarState = localStorage.getItem("techchef_sidebar");

    if (sidebarState === "collapsed") {
        body.classList.add("sidebar-collapsed");
    }

    sidebarToggle.addEventListener("click", function () {
        body.classList.toggle("sidebar-collapsed");

        if (body.classList.contains("sidebar-collapsed")) {
            localStorage.setItem("techchef_sidebar", "collapsed");
        } else {
            localStorage.setItem("techchef_sidebar", "expanded");
        }
    });
});