#!/bin/bash
# scripts/setup_rpi.sh - Run this ON RPi to setup everything

echo "🤖 Setting up Raspberry Pi for Robot Delivery System..."

# Get robot ID from command line or prompt
ROBOT_ID=${1:-}
if [ -z "$ROBOT_ID" ]; then
    echo "Enter Robot ID (e.g., Robot_001):"
    read ROBOT_ID
fi

echo "Setting up $ROBOT_ID..."

# Update system
echo "📦 Updating system..."
sudo apt update
sudo apt upgrade -y

# Install dependencies
echo "📦 Installing dependencies..."
sudo apt install -y python3 python3-pip python3-rpi.gpio git

# Install Python packages
echo "📦 Installing Python packages..."
pip3 install requests

# Clone or update repository
if [ ! -d "robot-delivery-system" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/YOUR_USERNAME/robot-delivery-system.git
else
    echo "📥 Updating repository..."
    cd robot-delivery-system
    git pull
    cd ..
fi

cd robot-delivery-system

# Generate robot-specific config
echo "⚙️  Generating config for $ROBOT_ID..."
python3 scripts/generate_robot_config.py $ROBOT_ID

echo ""
echo "✅ Setup complete for $ROBOT_ID!"
echo ""
echo "🎯 To start the robot:"
echo "   cd robot-delivery-system"
echo "   python3 run_robot.py"
echo ""
echo "🎯 To run in background:"
echo "   nohup python3 run_robot.py > robot.log 2>&1 &"
echo ""