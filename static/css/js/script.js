// Data check karein ke blank to nahi aa raha
console.log("User Data Received:", userData);

// Common Chart Options
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'bottom',
            labels: { 
                usePointStyle: true, 
                padding: 20,
                font: { family: "'Inter', sans-serif", size: 12 }
            }
        },
        tooltip: {
            backgroundColor: '#1a1a1a',
            padding: 12,
            titleFont: { size: 14 },
            callbacks: {
                label: function(context) {
                    return ` Spent: $${context.raw}`;
                }
            }
        }
    }
};

// 1. Bar Chart (Usage Analytics)
const ctxBar = document.getElementById('barChart');
if (ctxBar) {
    new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: userData.labels.length > 0 ? userData.labels : ["No Users Registered"],
            datasets: [{
                label: 'Spent Amount ($)',
                // Agar spent 0 ho toh dummy small value (0.1) dena taake bar nazar aaye, warna raw data
                data: userData.spent.length > 0 ? userData.spent.map(v => v === 0 ? 0.5 : v) : [0],
                backgroundColor: '#0d6efd',
                hoverBackgroundColor: '#0b5ed7',
                borderRadius: 10,
                borderSkipped: false,
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: { 
                    beginAtZero: true, 
                    grid: { color: '#f0f0f0', drawBorder: false },
                    ticks: { callback: value => '$' + value }
                },
                x: { 
                    grid: { display: false } 
                }
            }
        }
    });
}

// 2. Pie Chart (Expense Mix)
const ctxPie = document.getElementById('pieChart');
if (ctxPie) {
    const isAllZero = userData.spent.reduce((a, b) => a + b, 0) === 0;
    
    new Chart(ctxPie, {
        type: 'doughnut',
        data: {
            labels: userData.labels.length > 0 ? userData.labels : ["Empty Ledger"],
            datasets: [{
                // Agar sab 0 spent hain, toh barabar ka slice dikhao (visual demo ke liye)
                data: isAllZero ? userData.labels.map(() => 1) : userData.spent,
                backgroundColor: [
                    '#0d6efd', '#6610f2', '#0dcaf0', '#fd7e14', '#20c997', '#ffc107'
                ],
                hoverOffset: 20,
                borderWidth: 4,
                borderColor: '#ffffff'
            }]
        },
        options: {
            ...commonOptions,
            cutout: '70%',
            plugins: {
                ...commonOptions.plugins,
                tooltip: {
                    enabled: !isAllZero // Agar data real hai toh tooltip dikhao
                }
            }
        }
    });
}