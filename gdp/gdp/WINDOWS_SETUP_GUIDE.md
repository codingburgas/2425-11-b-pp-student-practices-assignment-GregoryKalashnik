# 🪟 Windows Installation Guide - University Admission Predictor

**Complete setup guide for Windows 10/11 users**

This guide will help you set up and run the University Admission Predictor Platform on your Windows computer. No prior programming experience required!

## 📋 What You'll Need

- Windows 10 or Windows 11
- Internet connection
- About 15 minutes of setup time
- Administrator access (for Python installation)

## 🎯 Step-by-Step Installation

### **Step 1: Install Python** ⚡

1. **Go to Python's official website**: [python.org/downloads](https://www.python.org/downloads/)

2. **Download Python 3.8 or newer** (look for the big yellow "Download Python" button)

3. **Run the installer** with these IMPORTANT settings:
   - ✅ **Check "Add Python to PATH"** (very important!)
   - ✅ **Check "Install for all users"** (recommended)
   - Click **"Install Now"**

4. **Verify installation**: 
   - Press `Windows + R` keys
   - Type `cmd` and press Enter
   - In the black window, type: `python --version`
   - You should see something like: `Python 3.11.2`

### **Step 2: Download the Project** 📁

**Option A: Download ZIP (Easiest)**
1. Download the project ZIP file from your source
2. Right-click the ZIP file → "Extract All"
3. Extract to a folder like: `C:\Users\YourName\Desktop\admission-predictor`

**Option B: If you have Git**
```cmd
git clone [your-repository-url]
cd admission-predictor
```

### **Step 3: Open Command Prompt in Project Folder** 💻

1. **Navigate to your project folder** in Windows Explorer
2. **Hold Shift + Right-click** in the empty space
3. **Select "Open PowerShell window here"** or "Open command window here"
4. You should see a command prompt in your project folder

### **Step 4: Set Up Virtual Environment** (Recommended) 🔒

In the command window, type these commands one by one:

```cmd
# Create a virtual environment
python -m venv admission_env

# Activate it
admission_env\Scripts\activate
```

**Success indicator**: Your command prompt should now show `(admission_env)` at the beginning.

### **Step 5: Install Required Packages** 📦

With the virtual environment active, run:

```cmd
pip install -r requirements.txt
```

**If you get errors**, try installing packages individually:
```cmd
pip install flask
pip install numpy
pip install scikit-learn
pip install joblib
pip install werkzeug
```

### **Step 6: Start the Application** 🚀

```cmd
python app.py
```

**You should see:**
```
Model trained with 2000 samples
Admission rate: 55.35%
Model accuracy: 0.765
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### **Step 7: Open in Browser** 🌐

1. **Open your web browser** (Chrome, Firefox, Edge)
2. **Go to**: `http://localhost:5000`
3. **You should see the landing page!** 🎉

## 🎮 How to Use

### **First Time Setup**

1. **Admin Login** (to test everything works):
   - Click "Login" 
   - Username: `admin`
   - Password: `admin123`
   - You'll see the admin dashboard

2. **Create Student Account**:
   - Logout from admin
   - Click "Register" 
   - Fill in your details
   - Start making predictions!

### **Daily Usage**

1. **Start the application**:
   ```cmd
   cd your-project-folder
   admission_env\Scripts\activate
   python app.py
   ```

2. **Open browser**: `http://localhost:5000`

3. **Stop the application**: Press `Ctrl+C` in the command window

## 🛠️ Troubleshooting Common Issues

### ❌ "Python is not recognized"
**Solution**: 
- Reinstall Python and make sure to check "Add Python to PATH"
- Restart your computer after installation
- Try using `py` instead of `python`

### ❌ "pip is not recognized"
**Solution**:
- Same as above - reinstall Python with PATH option
- Alternative: use `python -m pip install [package_name]`

### ❌ "Port 5000 is already in use"
**Solutions**:
- Close any other applications
- Or edit `app.py` and change `port=5000` to `port=5001`

### ❌ Permission errors
**Solutions**:
- Run Command Prompt as Administrator (right-click → "Run as administrator")
- Or install Python for current user only

### ❌ Virtual environment won't activate
**Try these alternatives**:
```cmd
admission_env\Scripts\activate.bat
# or
admission_env\Scripts\Activate.ps1
```

### ❌ Browser shows "This site can't be reached"
**Check**:
- Is the Python app still running? (look for the Flask output)
- Try `http://127.0.0.1:5000` instead of `localhost:5000`
- Make sure Windows Firewall isn't blocking the connection

## 📱 Features Overview

### **For Students**:
- ✅ Register your own account
- ✅ Enter GPA (0.0-4.0) and test scores (200-1600)
- ✅ Get AI-powered admission predictions
- ✅ View prediction history and analytics
- ✅ Update your profile information

### **For Administrators**:
- ✅ View all student data
- ✅ Edit student information
- ✅ Monitor system-wide analytics
- ✅ View all predictions across users
- ✅ System configuration options

## 🔧 Technical Information

### **What's Under the Hood**:
- **Language**: Python 3.8+
- **Web Framework**: Flask
- **Machine Learning**: Logistic Regression (scikit-learn)
- **Database**: SQLite (no setup required)
- **AI Model Accuracy**: 76.5%

### **File Structure**:
```
your-project-folder/
├── app.py                 # Main application file
├── requirements.txt       # List of required packages
├── admission_predictor.db # Database (created automatically)
└── templates/             # Web page templates
    ├── landing.html
    ├── login.html
    ├── student_dashboard.html
    └── admin_dashboard.html
```

## 🎓 Perfect for Academic Projects

This platform is ideal for:
- ✅ Computer Science final projects
- ✅ Machine Learning coursework demonstrations  
- ✅ Web development portfolio pieces
- ✅ Understanding Flask and ML integration
- ✅ Database design and user management systems

## 💡 Tips for Success

1. **Always activate your virtual environment** before running the app
2. **Keep the command window open** while using the website
3. **Use Chrome or Firefox** for best compatibility
4. **The database file is created automatically** - don't delete it!
5. **All student data is saved locally** on your computer

## 📞 Quick Reference Commands

```cmd
# Navigate to project folder
cd C:\path\to\your\project

# Activate virtual environment  
admission_env\Scripts\activate

# Start the application
python app.py

# Stop the application
Ctrl+C

# Deactivate virtual environment
deactivate
```

## 🎉 You're All Set!

Your University Admission Predictor Platform is now ready to use on Windows! 

**Access URL**: `http://localhost:5000`
**Admin Login**: `admin` / `admin123`

**Good luck with your finals project!** 🎓✨

---

*Need help? Check the troubleshooting section above or ensure all steps were followed correctly.* 