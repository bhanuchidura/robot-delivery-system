#!/bin/bash
# scripts/update_robot.sh - Run this ON RPi to update code

echo "🔄 Updating robot system..."

cd robot-delivery-system

# Pull latest code
echo "📥 Pulling latest code..."
git pull

# Restart the robot
echo "🔄 Restarting robot..."
pkill -f "python3 run_robot.py"
sleep 2
nohup python3 run_robot.py > robot.log 2>&1 &

echo "✅ Update complete! Check robot.log for status."