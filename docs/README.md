# Heart Disease Prediction Web Interface

This web interface provides a user-friendly way to test the heart disease prediction model. It's designed to be deployed on GitHub Pages for easy access and demonstration.

## Files

- `index.html` - Main web page with prediction form
- `styles.css` - Responsive styling and animations
- `script.js` - JavaScript functionality and API integration

## Features

- 🏥 **Medical-themed Design** - Professional healthcare appearance
- 📱 **Responsive Layout** - Works on desktop, tablet, and mobile
- 🧪 **Sample Data** - Pre-filled test data for quick demonstration
- ⚡ **Real-time Validation** - Form validation with visual feedback
- 🎯 **Mock Predictions** - Works without backend for demonstration
- 🔗 **API Ready** - Easy configuration for production API

## Local Testing

1. Open `index.html` in a web browser
2. The interface works with mock predictions for demonstration
3. Use "Fill Sample Data" button to quickly test functionality
4. All form validation and UI interactions are fully functional

## GitHub Pages Setup

### Method 1: Using GitHub Interface

1. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Click on "Settings" tab
   - Scroll down to "Pages" section
   - Under "Source", select "Deploy from a branch"
   - Choose "main" branch
   - Select "/ (root)" or "/docs" folder
   - Click "Save"

2. **Access Your Website:**
   - GitHub will provide a URL like: `https://yourusername.github.io/heart-disease-prediction`
   - It may take a few minutes for the site to be available

### Method 2: Using GitHub Actions (Recommended)

1. **Create GitHub Pages workflow:**
   ```yaml
   # .github/workflows/pages.yml
   name: Deploy to GitHub Pages
   
   on:
     push:
       branches: [ main ]
     workflow_dispatch:
   
   permissions:
     contents: read
     pages: write
     id-token: write
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Setup Pages
           uses: actions/configure-pages@v4
         - name: Upload artifact
           uses: actions/upload-pages-artifact@v3
           with:
             path: './docs'
         - name: Deploy to GitHub Pages
           id: deployment
           uses: actions/deploy-pages@v4
   ```

2. **Enable GitHub Pages:**
   - Go to Settings > Pages
   - Select "GitHub Actions" as source

## Connecting to Real API

To connect the web interface to your deployed FastAPI service:

1. **Deploy your API** (using the Docker container or cloud service)

2. **Update Configuration** in `script.js`:
   ```javascript
   const API_BASE_URL = 'https://your-api-url.com'; // Your actual API URL
   let isLocalTesting = false; // Change to false for production
   ```

3. **Configure CORS** in your FastAPI application:
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourusername.github.io"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## Form Fields

The prediction form includes all required features for the ML model:

- **Age** - Patient age (29-77 years)
- **Sex** - Male (1) or Female (0)
- **Chest Pain Type** - 4 categories of chest pain
- **Resting Blood Pressure** - In mmHg (94-200)
- **Cholesterol** - In mg/dl (126-564)
- **Fasting Blood Sugar** - >120 mg/dl (1) or ≤120 mg/dl (0)
- **Resting ECG** - 3 categories of ECG results
- **Maximum Heart Rate** - Achieved during exercise (71-202)
- **Exercise Induced Angina** - Yes (1) or No (0)
- **ST Depression** - Exercise vs rest (0.0-6.2)
- **Slope** - Peak exercise ST segment slope
- **Major Vessels** - Number colored by fluoroscopy (0-3)
- **Thalassemia** - Blood disorder type

## Mock Prediction Logic

When in local testing mode, the interface uses a mock prediction algorithm that considers:

- Age factors (higher risk for older patients)
- Gender factors (males typically higher risk)
- Chest pain symptoms
- Blood pressure levels
- Cholesterol levels
- Exercise-induced symptoms
- Cardiac imaging results

This provides realistic demo results for testing and presentation purposes.

## Customization

### Styling
- Modify CSS custom properties in `styles.css` for color scheme changes
- Update medical icons and branding as needed
- Adjust responsive breakpoints for different devices

### Functionality
- Add additional validation rules in `script.js`
- Customize result display format
- Add data visualization charts
- Implement result history tracking

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Security Notes

- No sensitive data is stored locally
- All predictions are processed client-side in demo mode
- HTTPS required for production API connections
- Input validation prevents malicious data submission

## Troubleshooting

### GitHub Pages not updating
- Check that the source branch and folder are correctly configured
- Clear browser cache
- Wait up to 10 minutes for changes to propagate

### API Connection Issues
- Verify CORS configuration on your API
- Check that API_BASE_URL is correct
- Ensure API is running and accessible
- Check browser console for error messages

### Form Validation Errors
- All fields are required for prediction
- Numeric fields have specific ranges
- Use sample data to test functionality

## Demo URL

Once deployed, your web interface will be available at:
`https://yourusername.github.io/heart-disease-prediction`

Replace `yourusername` with your actual GitHub username.