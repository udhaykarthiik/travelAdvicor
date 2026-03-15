from fpdf import FPDF
from datetime import datetime

def generate_itinerary_pdf(destination, days, budget, trip_type, itinerary, tips, events, gems):
    """Generate simple text content for PDF"""
    
    content = f"TRAVEL ITINERARY - {destination.upper()}\n"
    content += f"Generated: {datetime.now().strftime('%B %d, %Y')}\n"
    content += "=" * 50 + "\n\n"
    
    content += f"Trip Duration: {days} days\n"
    content += f"Budget: {budget.capitalize()}\n"
    content += f"Travel Type: {trip_type.capitalize()}\n\n"
    
    if tips:
        content += "TRAVEL TIPS:\n"
        for tip in tips:
            content += f"- {tip}\n"
        content += "\n"
    
    content += "DAY-BY-DAY ITINERARY:\n"
    content += "-" * 50 + "\n"
    
    for day in itinerary:
        content += f"\nDay {day.get('day', 'N/A')}:\n"
        content += f"Morning: {day.get('morning', 'N/A')}\n"
        content += f"Afternoon: {day.get('afternoon', 'N/A')}\n"
        content += f"Evening: {day.get('evening', 'N/A')}\n"
        content += f"Food: {day.get('food_suggestion', 'N/A')}\n"
        content += f"Stay: {day.get('accommodation_tip', 'TBD')}\n"
    
    if events:
        content += "\n\nLOCAL EVENTS:\n"
        content += "-" * 50 + "\n"
        for event in events:
            content += f"\n{event.get('event', 'Event')}\n"
            content += f"Location: {event.get('location', 'TBD')}\n"
            content += f"Dates: {event.get('dates', 'TBD')}\n"
            content += f"Type: {event.get('type', 'Event')}\n"
    
    if gems:
        content += "\n\nHIDDEN GEMS:\n"
        content += "-" * 50 + "\n"
        for gem in gems:
            content += f"\n{gem.get('name', 'Gem')}\n"
            content += f"{gem.get('description', 'No description')}\n"
            content += f"Best Time: {gem.get('best_time', 'Any')}\n"
            content += f"Location: {gem.get('location', 'TBD')}\n"
    
    content += "\n\n" + "=" * 50 + "\n"
    content += "Travel Advisor - Your Personal Trip Planner\n"
    content += "© 2026 Travel Advisor\n"
    
    return content

def create_pdf(content, output_path):
    """Create simple PDF from text content"""
    try:
        print(f"📝 Creating PDF at: {output_path}")
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        # Set margins
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.set_top_margin(15)
        
        # Add content line by line
        lines = content.split('\n')
        for line in lines:
            # Remove special characters that fpdf might have trouble with
            line = line.replace('•', '-').replace('℃', 'C')
            
            # Skip very long lines by truncating them
            if len(line) > 180:
                line = line[:177] + "..."
            
            try:
                pdf.cell(0, 5, txt=line.encode('latin-1', 'ignore').decode('latin-1'), ln=True)
            except:
                # If even that fails, just skip the line
                pass
        
        pdf.output(output_path)
        print(f"✅ PDF created successfully at {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ PDF creation error: {e}")
        import traceback
        traceback.print_exc()
        raise e