// Helper to format currency
const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
};

// Helper to show notifications
const showNotification = (message, type = 'info') => {
    // Simple alert for now, could be enhanced with a toast library
    alert(message);
};

// Dashboard Logic
const initDashboard = async () => {
    const statsContainer = document.getElementById('stats-container');
    if (!statsContainer) return;

    try {
        const response = await fetch('/api/stats');
        const data = await response.json();

        document.getElementById('total-predictions').textContent = data.total_predictions.toLocaleString();
        document.getElementById('fraud-detected').textContent = data.fraud_detected.toLocaleString();
        document.getElementById('accuracy').textContent = (data.accuracy * 100).toFixed(2) + '%';
        document.getElementById('last-update').textContent = data.last_update;

    } catch (error) {
        console.error('Error fetching stats:', error);
        statsContainer.innerHTML = '<p class="text-danger">Failed to load statistics.</p>';
    }
};

// Prediction Logic
const initPrediction = () => {
    const predictForm = document.getElementById('predict-form');
    const batchForm = document.getElementById('batch-form');
    const resultSection = document.getElementById('result-section');
    const batchResultSection = document.getElementById('batch-result-section');

    if (predictForm) {
        predictForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = predictForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            
            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loader"></span> Processing...';
                resultSection.classList.add('hidden');

                const formData = new FormData(predictForm);
                const data = Object.fromEntries(formData.entries());
                
                // Convert numeric strings to numbers
                for (let key in data) {
                    if (key !== 'type') {
                        data[key] = parseFloat(data[key]);
                    }
                }

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
                    showNotification(result.error || 'Prediction failed', 'error');
                }

            } catch (error) {
                console.error('Error:', error);
                showNotification('An unexpected error occurred', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }

    if (batchForm) {
        const fileInput = document.getElementById('csv-file');
        const uploadArea = document.querySelector('.file-upload');

        // Drag and drop handlers
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => uploadArea.classList.remove('dragover'), false);
        });

        uploadArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
            handleFiles(files);
        }

        fileInput.addEventListener('change', function() {
            handleFiles(this.files);
        });

        function handleFiles(files) {
            if (files.length > 0) {
                const fileName = files[0].name;
                document.getElementById('file-name').textContent = fileName;
                // Auto submit or enable submit button
            }
        }

        batchForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            if (!fileInput.files.length) {
                showNotification('Please select a file first', 'warning');
                return;
            }

            const submitBtn = batchForm.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;

            try {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loader"></span> Uploading...';
                batchResultSection.classList.add('hidden');

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                const response = await fetch('/api/predict-batch', {
                    method: 'POST',
                    body: formData
                });

                const result = await response.json();

                if (response.ok) {
                    displayBatchResult(result);
                } else {
                    showNotification(result.error || 'Batch prediction failed', 'error');
                }

            } catch (error) {
                console.error('Error:', error);
                showNotification('An unexpected error occurred', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    }
};

const displayResult = (data) => {
    const resultSection = document.getElementById('result-section');
    const resultCard = document.getElementById('result-card');
    const resultTitle = document.getElementById('result-title');
    const resultProb = document.getElementById('result-probability');
    const resultRisk = document.getElementById('result-risk');

    resultSection.classList.remove('hidden');
    resultSection.scrollIntoView({ behavior: 'smooth' });

    const isFraud = data.result.is_fraud;
    const riskLevel = data.result.risk_level;

    if (isFraud) {
        resultTitle.textContent = 'FRAUD DETECTED';
        resultTitle.className = 'text-danger mb-2';
        resultCard.style.borderColor = 'var(--danger)';
    } else {
        resultTitle.textContent = 'TRANSACTION SAFE';
        resultTitle.className = 'text-success mb-2';
        resultCard.style.borderColor = 'var(--success)';
    }

    resultProb.textContent = `Probability: ${(data.result.fraud_probability * 100).toFixed(2)}%`;
    resultRisk.textContent = `Risk Level: ${riskLevel}`;
    resultRisk.className = `risk-badge risk-${riskLevel.toLowerCase()}`;
};

const displayBatchResult = (data) => {
    const section = document.getElementById('batch-result-section');
    const summary = document.getElementById('batch-summary');
    const tableBody = document.getElementById('batch-table-body');

    section.classList.remove('hidden');
    
    summary.innerHTML = `
        <div class="card mb-4">
            <h3>Batch Summary</h3>
            <div class="grid grid-3">
                <div>
                    <p class="text-muted">Total Transactions</p>
                    <p class="h3">${data.total_transactions}</p>
                </div>
                <div>
                    <p class="text-muted">Fraud Detected</p>
                    <p class="h3 text-danger">${data.fraud_detected}</p>
                </div>
                <div>
                    <p class="text-muted">Clean Transactions</p>
                    <p class="h3 text-success">${data.total_transactions - data.fraud_detected}</p>
                </div>
            </div>
        </div>
    `;

    tableBody.innerHTML = data.results.map(row => `
        <tr>
            <td>${row.is_fraud ? '<span class="text-danger">FRAUD</span>' : '<span class="text-success">SAFE</span>'}</td>
            <td>${(row.fraud_probability * 100).toFixed(1)}%</td>
            <td>${row.risk_level}</td>
        </tr>
    `).join('');
};

// Initialize based on page
document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    initPrediction();
});
