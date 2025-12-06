document.addEventListener('DOMContentLoaded', () => {
    // Support both index.html (predictionForm) and predict.html (predict-form)
    const form = document.getElementById('predict-form') || document.getElementById('predictionForm');
    const resultSection = document.getElementById('result-section') || document.getElementById('resultSection');
    const statusBadge = document.getElementById('statusBadge');
    const riskScoreText = document.getElementById('riskScoreText');

    // Only run if form exists
    if (!form) return;

    let riskChart = null;
    let reasonsChart = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading state
        const btn = form.querySelector('button');
        const originalBtnText = btn.innerHTML;
        btn.innerHTML = 'Analyzing...';
        btn.disabled = true;

        // Gather data
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        // Convert numbers
        for (const key in data) {
            if (key !== 'type') {
                data[key] = parseFloat(data[key]);
            }
        }

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (response.ok) {
                displayResult(result);
            } else {
                alert('Error: ' + (result.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred during prediction.');
        } finally {
            btn.innerHTML = originalBtnText;
            btn.disabled = false;
        }
    });

    function displayResult(data) {
        // Show result section
        resultSection.classList.remove('hidden');

        // Update Status Badge
        if (data.is_fraud === 1) {
            statusBadge.textContent = 'HIGH RISK';
            statusBadge.className = 'status-badge status-fraud';
        } else {
            statusBadge.textContent = 'SAFE';
            statusBadge.className = 'status-badge status-safe';
        }

        // Update Risk Score Text
        riskScoreText.textContent = `${Math.round(data.risk_score)}%`;

        // Render Charts
        renderRiskChart(data.risk_score);
        renderReasonsChart(data.reasons);

        // Scroll to result on mobile
        if (window.innerWidth < 900) {
            resultSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    function renderRiskChart(score) {
        const ctx = document.getElementById('riskChart').getContext('2d');

        if (riskChart) {
            riskChart.destroy();
        }

        const color = score > 50 ? '#ff7675' : '#00b894';
        const emptyColor = 'rgba(255, 255, 255, 0.1)';

        riskChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Risk', 'Safe'],
                datasets: [{
                    data: [score, 100 - score],
                    backgroundColor: [color, emptyColor],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                cutout: '75%',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                }
            }
        });
    }

    function renderReasonsChart(reasons) {
        const ctx = document.getElementById('reasonsChart').getContext('2d');

        if (reasonsChart) {
            reasonsChart.destroy();
        }

        const labels = reasons.map(r => r.feature);
        const data = reasons.map(r => Math.abs(r.impact)); // Use absolute impact for visualization length

        reasonsChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'SHAP Impact',
                    data: data,
                    backgroundColor: 'rgba(157, 78, 221, 0.6)',
                    borderColor: '#9d4edd',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.1)' },
                        ticks: { color: '#a0a0a0' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#ffffff' }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }
});
