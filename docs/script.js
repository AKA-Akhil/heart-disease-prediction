// Global variables
const API_BASE_URL = 'https://your-api-url.com'; // Replace with your actual API URL
let isLocalTesting = true; // Set to false when you have a deployed API

// DOM elements
const predictionForm = document.getElementById('predictionForm');
const resultsContainer = document.getElementById('results');
const predictBtn = document.getElementById('predictBtn');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
    setupNavigation();
});

// Event listeners
function setupEventListeners() {
    predictionForm.addEventListener('submit', handlePrediction);
    
    // Add input validation
    const inputs = predictionForm.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('change', validateInput);
    });
}

// Navigation setup
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                scrollToSection(targetId);
                
                // Update active nav link
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
            }
        });
    });
    
    // Handle scroll to update active nav
    window.addEventListener('scroll', updateActiveNav);
}

// Smooth scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        const headerHeight = document.querySelector('.header').offsetHeight;
        const targetPosition = section.offsetTop - headerHeight - 20;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    }
}

// Update active navigation on scroll
function updateActiveNav() {
    const sections = ['home', 'predict', 'about'];
    const scrollPosition = window.scrollY + 100;
    
    sections.forEach(sectionId => {
        const section = document.getElementById(sectionId);
        const navLink = document.querySelector(`a[href="#${sectionId}"]`);
        
        if (section && navLink) {
            const sectionTop = section.offsetTop;
            const sectionBottom = sectionTop + section.offsetHeight;
            
            if (scrollPosition >= sectionTop && scrollPosition < sectionBottom) {
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                navLink.classList.add('active');
            }
        }
    });
}

// Handle prediction form submission
async function handlePrediction(e) {
    e.preventDefault();
    
    // Show loading state
    showLoading(true);
    hideResults();
    
    try {
        // Collect form data
        const formData = collectFormData();
        
        // Validate data
        if (!validateFormData(formData)) {
            showError('Please fill in all required fields correctly.');
            return;
        }
        
        // Make prediction
        const result = await makePrediction(formData);
        
        // Display results
        displayResults(result);
        
    } catch (error) {
        console.error('Prediction error:', error);
        showError('Sorry, there was an error making the prediction. Please try again.');
    } finally {
        showLoading(false);
    }
}

// Collect form data
function collectFormData() {
    const formData = {};
    const inputs = predictionForm.querySelectorAll('input, select');
    
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
    
    // Additional validation
    if (data.age < 1 || data.age > 120) return false;
    if (data.trestbps < 80 || data.trestbps > 200) return false;
    if (data.chol < 100 || data.chol > 600) return false;
    if (data.thalach < 60 || data.thalach > 220) return false;
    if (data.oldpeak < 0 || data.oldpeak > 10) return false;
    
    return true;
}

// Make prediction (mock for demo, replace with actual API call)
async function makePrediction(data) {
    if (isLocalTesting) {
        // Mock prediction for demonstration
        return mockPrediction(data);
    } else {
        // Actual API call
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
}

// Mock prediction for demonstration
function mockPrediction(data) {
    return new Promise(resolve => {
        setTimeout(() => {
            // Simple risk calculation based on key factors
            let riskScore = 0;
            
            // Age factor
            if (data.age > 60) riskScore += 0.3;
            else if (data.age > 45) riskScore += 0.2;
            
            // Sex factor (males typically higher risk)
            if (data.sex === 1) riskScore += 0.1;
            
            // Chest pain factor
            if (data.cp === 0) riskScore += 0.3; // Typical angina
            else if (data.cp === 1) riskScore += 0.2; // Atypical angina
            
            // Blood pressure
            if (data.trestbps > 140) riskScore += 0.2;
            
            // Cholesterol
            if (data.chol > 240) riskScore += 0.2;
            
            // Exercise induced angina
            if (data.exang === 1) riskScore += 0.3;
            
            // Major vessels
            if (data.ca > 0) riskScore += 0.2 * data.ca;
            
            // Thalassemia
            if (data.thal === 3) riskScore += 0.3; // Reversible defect
            
            // Add some randomness for demonstration
            riskScore += (Math.random() - 0.5) * 0.2;
            
            // Clamp between 0 and 1
            riskScore = Math.max(0, Math.min(1, riskScore));
            
            const prediction = riskScore > 0.5 ? 1 : 0;
            
            resolve({
                prediction: prediction,
                probability: riskScore,
                model_version: "demo-v1.0.0",
                timestamp: new Date().toISOString()
            });
        }, 2000); // Simulate API delay
    });
}

// Display prediction results
function displayResults(result) {
    const riskLevel = document.getElementById('riskLevel');
    const confidence = document.getElementById('confidence');
    const modelVersion = document.getElementById('modelVersion');
    const resultStatus = document.getElementById('resultStatus');
    
    // Set risk level
    const isHighRisk = result.prediction === 1;
    riskLevel.textContent = isHighRisk ? 'High Risk' : 'Low Risk';
    riskLevel.style.color = isHighRisk ? 'var(--error-color)' : 'var(--success-color)';
    
    // Set confidence
    const confidencePercentage = (result.probability * 100).toFixed(1);
    confidence.textContent = `${confidencePercentage}%`;
    confidence.style.color = isHighRisk ? 'var(--error-color)' : 'var(--success-color)';
    
    // Set model version
    modelVersion.textContent = result.model_version || 'Unknown';
    
    // Set status badge
    resultStatus.textContent = isHighRisk ? 'High Risk Detected' : 'Low Risk Detected';
    resultStatus.className = `result-status ${isHighRisk ? 'high-risk' : 'low-risk'}`;
    
    // Show results
    showResults();
    
    // Scroll to results
    setTimeout(() => {
        resultsContainer.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'nearest' 
        });
    }, 300);
}

// Validate individual input
function validateInput(e) {
    const input = e.target;
    const value = input.value;
    
    // Remove previous validation styling
    input.classList.remove('error');
    
    // Basic validation
    if (input.hasAttribute('required') && !value) {
        input.classList.add('error');
        return;
    }
    
    // Type-specific validation
    if (input.type === 'number') {
        const num = parseFloat(value);
        const min = parseFloat(input.getAttribute('min'));
        const max = parseFloat(input.getAttribute('max'));
        
        if (isNaN(num) || (min && num < min) || (max && num > max)) {
            input.classList.add('error');
        }
    }
}

// Fill sample data for testing
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
    
    showNotification('Sample data filled successfully!', 'success');
}

// Show/hide loading state
function showLoading(show) {
    if (show) {
        predictBtn.disabled = true;
        predictBtn.innerHTML = '<div class="loading"></div> Analyzing...';
    } else {
        predictBtn.disabled = false;
        predictBtn.innerHTML = '<i class="fas fa-brain"></i> Predict Risk';
    }
}

// Show/hide results
function showResults() {
    resultsContainer.style.display = 'block';
    resultsContainer.style.animation = 'fadeIn 0.5s ease-in';
}

function hideResults() {
    resultsContainer.style.display = 'none';
}

// Show error message
function showError(message) {
    showNotification(message, 'error');
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        box-shadow: var(--shadow-lg);
        z-index: 1001;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Add button styles
    const button = notification.querySelector('button');
    button.style.cssText = `
        background: transparent;
        border: none;
        color: white;
        cursor: pointer;
        padding: 0.25rem;
        margin-left: 0.5rem;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getNotificationColor(type) {
    const colors = {
        success: 'var(--success-color)',
        error: 'var(--error-color)',
        warning: 'var(--warning-color)',
        info: 'var(--primary-color)'
    };
    return colors[type] || 'var(--primary-color)';
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .form-group input.error,
    .form-group select.error {
        border-color: var(--error-color);
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
`;
document.head.appendChild(style);

// API Configuration Note
console.log(`
🏥 Heart Disease Prediction System
===================================

Current Mode: ${isLocalTesting ? 'LOCAL TESTING (Mock Predictions)' : 'PRODUCTION (Real API)'}

To connect to your actual API:
1. Deploy your FastAPI service
2. Update API_BASE_URL in script.js
3. Set isLocalTesting = false
4. Ensure CORS is configured properly

For local development:
- The app currently uses mock predictions
- All functionality works for demonstration
- Form validation is fully functional
- UI interactions are complete

GitHub Repository: https://github.com/AKA-Akhil/heart-disease-prediction
`);