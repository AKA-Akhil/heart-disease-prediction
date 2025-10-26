// Simple Heart Disease Prediction Script
const API_BASE_URL = 'https://your-api-url.com'; // Replace with your actual API URL
let isLocalTesting = true; // Set to false when you have a deployed API

// DOM elements
const form = document.getElementById('predictionForm');
const resultsDiv = document.getElementById('results');
const predictBtn = document.getElementById('predictBtn');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    form.addEventListener('submit', handlePrediction);
});

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