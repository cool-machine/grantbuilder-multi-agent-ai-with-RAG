#!/bin/bash
# Cost Control Script for Azure ML Testing

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔧 Azure ML Cost Control${NC}"
echo "========================="

# Function to check compute status
check_compute_status() {
    echo -e "\n📊 Checking compute instance status..."
    STATUS=$(az ml compute show --name "multi-model-test" --resource-group ocp10 --workspace-name ocp10 --query "state" -o tsv 2>/dev/null)
    
    if [ "$STATUS" = "Running" ]; then
        echo -e "Status: ${GREEN}Running${NC} 💸 (billing active)"
        
        # Get current cost estimate
        HOURS=$(az ml compute show --name "multi-model-test" --resource-group ocp10 --workspace-name ocp10 --query "properties.createdOn" -o tsv)
        echo -e "💰 Estimated cost today: ~$7.20/hour of usage"
        
    elif [ "$STATUS" = "Stopped" ]; then
        echo -e "Status: ${YELLOW}Stopped${NC} ✅ (no billing)"
        
    elif [ "$STATUS" = "Starting" ]; then
        echo -e "Status: ${YELLOW}Starting${NC} ⏳"
        
    elif [ "$STATUS" = "Stopping" ]; then
        echo -e "Status: ${YELLOW}Stopping${NC} ⏳"
        
    else
        echo -e "Status: ${RED}Unknown (${STATUS})${NC}"
    fi
}

# Function to start compute
start_compute() {
    echo -e "\n🚀 Starting compute instance..."
    az ml compute start --name "multi-model-test" --resource-group ocp10 --workspace-name ocp10
    echo -e "${GREEN}✅ Compute instance starting (will take 2-3 minutes)${NC}"
    echo -e "${YELLOW}⚠️  Remember to stop when done to avoid charges!${NC}"
}

# Function to stop compute
stop_compute() {
    echo -e "\n⏹️  Stopping compute instance..."
    az ml compute stop --name "multi-model-test" --resource-group ocp10 --workspace-name ocp10
    echo -e "${GREEN}✅ Compute instance stopped - billing stopped${NC}"
}

# Function to show cost estimates
show_costs() {
    echo -e "\n💰 Cost Estimates (Standard_E32s_v3):"
    echo "======================================"
    echo "Hourly: $2.40"
    echo "2-hour session: $4.80"
    echo "4-hour session: $9.60"
    echo "8-hour session: $19.20"
    echo ""
    echo "Monthly estimates:"
    echo "• 1 session/week (2h): $19.20/month"
    echo "• 2 sessions/week (2h): $38.40/month"
    echo "• Daily testing (2h): $144/month"
    echo ""
    echo -e "${YELLOW}💡 Pro tip: Always stop after testing!${NC}"
}

# Function to set auto-stop reminder
set_reminder() {
    echo -e "\n⏰ Setting 2-hour auto-reminder..."
    (sleep 7200 && notify-send "Azure ML" "Remember to stop your compute instance!" 2>/dev/null || echo -e "${YELLOW}🔔 REMINDER: Stop your compute instance to avoid charges!${NC}") &
    echo -e "${GREEN}✅ Reminder set for 2 hours${NC}"
}

# Main menu
case "$1" in
    "status")
        check_compute_status
        ;;
    "start")
        start_compute
        set_reminder
        ;;
    "stop")
        stop_compute
        ;;
    "costs")
        show_costs
        ;;
    *)
        echo "Usage: $0 {status|start|stop|costs}"
        echo ""
        echo "Commands:"
        echo "  status  - Check if compute instance is running"
        echo "  start   - Start compute instance (begins billing)"
        echo "  stop    - Stop compute instance (stops billing)"
        echo "  costs   - Show cost estimates"
        echo ""
        check_compute_status
        show_costs
        ;;
esac