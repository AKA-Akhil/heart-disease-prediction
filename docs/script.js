// Simple Heart Disease Prediction Script with CI/CD Integration
const API_BASE_URL = 'https://your-api-url.com'; // Replace with your actual API URL
const GITHUB_API_BASE = 'https://api.github.com/repos/AKA-Akhil/heart-disease-prediction';
let isLocalTesting = true; // Set to false when you have a deployed API

// DOM elements
const form = document.getElementById('predictionForm');
const resultsDiv = document.getElementById('results');
const predictBtn = document.getElementById('predictBtn');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    form.addEventListener('submit', handlePrediction);
    initializePipelineStatus();
    initializeCopyButtons();
});

// Initialize copy buttons
function initializeCopyButtons() {
    console.log('🚀 Initializing copy buttons...');
    
    // Test copy buttons after a short delay
    setTimeout(() => {
        testCopyButtons();
    }, 100);
    
    // Add click listeners to copy buttons as backup
    const copyButtons = document.querySelectorAll('.copy-btn');
    copyButtons.forEach((btn, index) => {
        console.log(`Found copy button ${index + 1}:`, btn);
        
        // Add event listener as backup to onclick
        btn.addEventListener('click', function(event) {
            console.log('🖱️ Copy button clicked via event listener');
            event.preventDefault();
            
            const input = btn.previousElementSibling;
            if (input && input.tagName === 'INPUT') {
                console.log('Copy button clicked, copying:', input.value);
                copyToClipboard(input.id);
            } else {
                console.error('Could not find input field for copy button');
            }
        });
        
        // Also test the onclick attribute
        btn.addEventListener('mouseenter', function() {
            console.log('Mouse entered copy button, onclick attr:', btn.getAttribute('onclick'));
        });
    });
}

// Initialize pipeline status monitoring
async function initializePipelineStatus() {
    try {
        await updatePipelineStatus();
        await updateCommitInfo();
        
        // Update every 30 seconds
        setInterval(updatePipelineStatus, 30000);
    } catch (error) {
        console.warn('Pipeline status unavailable (demo mode)', error);
        showDemoStatus();
    }
}

// Update pipeline status from GitHub Actions
async function updatePipelineStatus() {
    try {
        const response = await fetch(`${GITHUB_API_BASE}/actions/runs?per_page=1`);
        const data = await response.json();
        
        if (data.workflow_runs && data.workflow_runs.length > 0) {
            const latestRun = data.workflow_runs[0];
            updatePipelineUI(latestRun);
        }
    } catch (error) {
        console.warn('Could not fetch pipeline status:', error);
    }
}

// Update commit information
async function updateCommitInfo() {
    try {
        const response = await fetch(`${GITHUB_API_BASE}/commits?per_page=1`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            const latestCommit = data[0];
            document.getElementById('commitSha').textContent = latestCommit.sha.substring(0, 8);
            
            const commitDate = new Date(latestCommit.commit.committer.date);
            document.getElementById('lastTrained').textContent = commitDate.toLocaleDateString();
        }
    } catch (error) {
        console.warn('Could not fetch commit info:', error);
    }
}

// Update pipeline UI based on GitHub Actions data
function updatePipelineUI(workflowRun) {
    const stages = ['test', 'train', 'build', 'deploy'];
    const status = workflowRun.status;
    const conclusion = workflowRun.conclusion;
    
    // Reset all stages
    stages.forEach(stage => {
        const element = document.getElementById(`${stage}-stage`);
        const statusElement = document.getElementById(`${stage}-status`);
        
        element.className = 'stage';
        statusElement.textContent = '⏳';
    });
    
    // Update based on workflow status
    if (status === 'in_progress') {
        // Simulate progress based on time (this is a simplified approach)
        updateRunningStatus();
    } else if (status === 'completed') {
        if (conclusion === 'success') {
            stages.forEach((stage, index) => {
                const element = document.getElementById(`${stage}-stage`);
                const statusElement = document.getElementById(`${stage}-status`);
                
                element.className = 'stage success';
                statusElement.textContent = '✅';
            });
        } else if (conclusion === 'failure') {
            // Mark stages as failed (simplified)
            stages.forEach((stage, index) => {
                const element = document.getElementById(`${stage}-stage`);
                const statusElement = document.getElementById(`${stage}-status`);
                
                if (index < 2) { // Assume failure in later stages
                    element.className = 'stage success';
                    statusElement.textContent = '✅';
                } else {
                    element.className = 'stage failed';
                    statusElement.textContent = '❌';
                    return; // Stop at first failure
                }
            });
        }
    }
}

// Show demo status when GitHub API is unavailable
function showDemoStatus() {
    const stages = ['test', 'train', 'build', 'deploy'];
    
    stages.forEach((stage, index) => {
        setTimeout(() => {
            const element = document.getElementById(`${stage}-stage`);
            const statusElement = document.getElementById(`${stage}-status`);
            
            element.className = 'stage success';
            statusElement.textContent = '✅';
        }, index * 1000);
    });
    
    document.getElementById('commitSha').textContent = 'demo-123';
    document.getElementById('lastTrained').textContent = new Date().toLocaleDateString();
    
    setTimeout(() => {
        enableContainerDownload('demo');
    }, 4000);
}

// Update running status animation
function updateRunningStatus() {
    const stages = ['test', 'train', 'build', 'deploy'];
    let currentStage = 0;
    
    const interval = setInterval(() => {
        if (currentStage < stages.length) {
            const stage = stages[currentStage];
            const element = document.getElementById(`${stage}-stage`);
            const statusElement = document.getElementById(`${stage}-status`);
            
            // Previous stages success
            for (let i = 0; i < currentStage; i++) {
                const prevStage = stages[i];
                document.getElementById(`${prevStage}-stage`).className = 'stage success';
                document.getElementById(`${prevStage}-status`).textContent = '✅';
            }
            
            // Current stage running
            element.className = 'stage running';
            statusElement.textContent = '⏳';
            
            currentStage++;
        } else {
            clearInterval(interval);
            // All stages complete
            stages.forEach(stage => {
                document.getElementById(`${stage}-stage`).className = 'stage success';
                document.getElementById(`${stage}-status`).textContent = '✅';
            });
        }
    }, 2000);
}

// Handle form submission
async function handlePrediction(e) {
    e.preventDefault();
    
    showLoading(true);
    hideResults();
    
    try {
        const formData = collectFormData();
        
        if (!validateFormData(formData)) {
            alert('Please fill in all fields correctly.');
            return;
        }
        
        const result = await makePrediction(formData);
        displayResults(result);
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error making prediction. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Collect form data
function collectFormData() {
    const formData = {};
    const inputs = form.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        if (input.name) {
            formData[input.name] = input.type === 'number' ? 
                parseFloat(input.value) : 
                parseInt(input.value);
        }
    });
    
    return formData;
}

// Validate form data
function validateFormData(data) {
    const requiredFields = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
        'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
    ];
    
    for (const field of requiredFields) {
        if (data[field] === undefined || data[field] === '' || isNaN(data[field])) {
            return false;
        }
    }
    
    return true;
}

// Make prediction
async function makePrediction(data) {
    if (isLocalTesting) {
        return mockPrediction(data);
    } else {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Mock prediction for demo
function mockPrediction(data) {
    return new Promise(resolve => {
        setTimeout(() => {
            // Simple risk calculation
            let riskScore = 0;
            
            if (data.age > 60) riskScore += 0.3;
            if (data.sex === 1) riskScore += 0.1;
            if (data.cp === 0) riskScore += 0.3;
            if (data.trestbps > 140) riskScore += 0.2;
            if (data.chol > 240) riskScore += 0.2;
            if (data.exang === 1) riskScore += 0.3;
            if (data.ca > 0) riskScore += 0.2 * data.ca;
            if (data.thal === 3) riskScore += 0.3;
            
            riskScore += (Math.random() - 0.5) * 0.2;
            riskScore = Math.max(0, Math.min(1, riskScore));
            
            const prediction = riskScore > 0.5 ? 1 : 0;
            
            resolve({
                prediction: prediction,
                probability: riskScore
            });
        }, 1500);
    });
}

// Display results
function displayResults(result) {
    const riskLevel = document.getElementById('riskLevel');
    const confidence = document.getElementById('confidence');
    
    const isHighRisk = result.prediction === 1;
    
    riskLevel.textContent = isHighRisk ? 'High Risk' : 'Low Risk';
    riskLevel.className = `value ${isHighRisk ? 'high-risk' : 'low-risk'}`;
    
    const confidencePercentage = (result.probability * 100).toFixed(1);
    confidence.textContent = `${confidencePercentage}%`;
    confidence.className = `value ${isHighRisk ? 'high-risk' : 'low-risk'}`;
    
    showResults();
}

// Fill sample data
function fillSampleData() {
    const sampleData = {
        age: 54,
        sex: 1,
        cp: 0,
        trestbps: 140,
        chol: 239,
        fbs: 0,
        restecg: 1,
        thalach: 160,
        exang: 0,
        oldpeak: 1.2,
        slope: 2,
        ca: 0,
        thal: 2
    };
    
    Object.keys(sampleData).forEach(key => {
        const input = document.getElementById(key);
        if (input) {
            input.value = sampleData[key];
        }
    });
}

// Show/hide loading
function showLoading(show) {
    if (show) {
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<div class="loading"></div>Analyzing...';
    } else {
        predictBtn.disabled = false;
        predictBtn.innerHTML = 'Predict';
    }
}

// Show/hide results
function showResults() {
    resultsDiv.style.display = 'block';
}

function hideResults() {
    resultsDiv.style.display = 'none';
}

// Copy command to clipboard
function copyToClipboard(elementId) {
    console.log('copyToClipboard called with elementId:', elementId);
    
    const element = document.getElementById(elementId);
    if (!element) {
        console.error('Element not found:', elementId);
        alert('Error: Could not find the text to copy');
        return;
    }
    
    const text = element.value;
    console.log('Text to copy:', text);
    
    // Show visual feedback immediately
    const copyBtn = element.nextElementSibling;
    if (!copyBtn) {
        console.error('Copy button not found');
        return;
    }
    
    const originalText = copyBtn.textContent;
    console.log('Copy button found, original text:', originalText);
    
    // Modern clipboard API (preferred)
    if (navigator.clipboard && window.isSecureContext) {
        console.log('Using modern clipboard API');
        navigator.clipboard.writeText(text).then(() => {
            console.log('✅ Text copied to clipboard using modern API');
            showCopyFeedback(copyBtn, originalText);
        }).catch(err => {
            console.error('❌ Modern clipboard API failed:', err);
            // Fallback to older method
            fallbackCopyToClipboard(element, copyBtn, originalText);
        });
    } else {
        console.log('Modern clipboard API not available, using fallback');
        // Fallback for older browsers or non-secure contexts
        fallbackCopyToClipboard(element, copyBtn, originalText);
    }
}

// Fallback copy method
function fallbackCopyToClipboard(element, copyBtn, originalText) {
    console.log('Using fallback copy method');
    try {
        element.focus();
        element.select();
        element.setSelectionRange(0, 99999); // For mobile devices
        
        const successful = document.execCommand('copy');
        console.log('document.execCommand result:', successful);
        
        if (successful) {
            console.log('✅ Text copied to clipboard using fallback method');
            showCopyFeedback(copyBtn, originalText);
        } else {
            throw new Error('Copy command failed');
        }
    } catch (err) {
        console.error('❌ Fallback copy failed:', err);
        // Last resort - show the text for manual copy
        const text = element.value;
        prompt('⚠️ Automatic copy failed. Please copy this command manually:', text);
    }
}

// Show copy feedback
function showCopyFeedback(copyBtn, originalText) {
    console.log('Showing copy feedback');
    copyBtn.textContent = 'Copied!';
    copyBtn.style.background = '#2196F3';
    copyBtn.style.transform = 'scale(0.95)';
    
    setTimeout(() => {
        copyBtn.textContent = originalText;
        copyBtn.style.background = '';
        copyBtn.style.transform = '';
        console.log('Reset copy button to original state');
    }, 2000);
}

// Test function to verify buttons work
function testCopyButtons() {
    console.log('🧪 Testing copy buttons...');
    const copyButtons = document.querySelectorAll('.copy-btn');
    console.log('Found copy buttons:', copyButtons.length);
    
    copyButtons.forEach((btn, index) => {
        console.log(`Button ${index + 1}:`, btn);
        console.log(`  - Text: "${btn.textContent}"`);
        console.log(`  - onclick: ${btn.getAttribute('onclick')}`);
        console.log(`  - Previous element (input): ${btn.previousElementSibling}`);
    });
}