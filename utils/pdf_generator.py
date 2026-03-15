from fpdf import FPDF
from datetime import datetime
import textwrap

class SimplePDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(26, 58, 92)
        self.cell(0, 10, 'Travel Advisor', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_itinerary_pdf(destination, days, budget, trip_type, itinerary, tips, events, gems, packing_list, output_path):
    """Generate a simple, reliable PDF - NO SPECIAL CHARACTERS"""
    
    pdf = SimplePDF()
    pdf.add_page()
    
    # Helper function to add text safely
    def add_text(text, indent=0):
        if not text:
            return
        # Convert to string and remove any non-ASCII characters
        safe_text = str(text).encode('ascii', 'ignore').decode('ascii')
        # Wrap text
        lines = textwrap.wrap(safe_text, width=70)
        for line in lines:
            if indent:
                pdf.cell(indent)
            pdf.cell(0, 5, line, 0, 1)
    
    # Title
    pdf.set_font('helvetica', 'B', 20)
    safe_dest = str(destination).encode('ascii', 'ignore').decode('ascii').upper()
    pdf.cell(0, 15, safe_dest, 0, 1, 'C')
    
    # Trip Info
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 8, f"{days} Days | {budget} Budget | {trip_type} Trip", 0, 1, 'C')
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%B %d, %Y')}", 0, 1, 'C')
    pdf.ln(10)
    
    # Travel Tips
    if tips:
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'TRAVEL TIPS', 0, 1)
        pdf.set_font('helvetica', '', 11)
        for tip in tips[:5]:
            add_text("- " + tip, indent=5)
        pdf.ln(5)
    
    # Itinerary
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, 'ITINERARY', 0, 1)
    
    for day in itinerary:
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, f"Day {day.get('day', '')}", 0, 1)
        
        pdf.set_font('helvetica', '', 11)
        if day.get('morning'):
            add_text("Morning: " + day.get('morning', ''), indent=5)
        if day.get('afternoon'):
            add_text("Afternoon: " + day.get('afternoon', ''), indent=5)
        if day.get('evening'):
            add_text("Evening: " + day.get('evening', ''), indent=5)
        if day.get('food_suggestion'):
            add_text("Food: " + day.get('food_suggestion', ''), indent=5)
        if day.get('accommodation_tip'):
            add_text("Stay: " + day.get('accommodation_tip', ''), indent=5)
        pdf.ln(3)
    
    # Local Events
    if events:
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'LOCAL EVENTS', 0, 1)
        
        pdf.set_font('helvetica', '', 11)
        for event in events[:8]:
            if event.get('event'):
                add_text("- " + event.get('event', ''))
            if event.get('location'):
                add_text("  Location: " + event.get('location', ''), indent=5)
            if event.get('dates'):
                add_text("  Dates: " + event.get('dates', ''), indent=5)
            pdf.ln(2)
    
    # Hidden Gems
    if gems:
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'HIDDEN GEMS', 0, 1)
        
        pdf.set_font('helvetica', '', 11)
        for gem in gems[:6]:
            if gem.get('name'):
                add_text("- " + gem.get('name', ''))
            if gem.get('description'):
                add_text("  " + gem.get('description', ''), indent=5)
            if gem.get('best_time'):
                add_text("  Best: " + gem.get('best_time', ''), indent=5)
            if gem.get('location'):
                add_text("  Location: " + gem.get('location', ''), indent=5)
            pdf.ln(2)
    
    # Packing List
    if packing_list:
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, 'PACKING LIST', 0, 1)
        
        for category, items in packing_list.items():
            if items:
                safe_cat = str(category).replace('_', ' ').title()
                pdf.set_font('helvetica', 'B', 12)
                pdf.cell(0, 8, safe_cat, 0, 1)
                
                pdf.set_font('helvetica', '', 11)
                for item in items[:8]:
                    clean_item = str(item).replace('✅', '').replace('✓', '').strip()
                    add_text("- " + clean_item, indent=5)
                pdf.ln(2)
    
    # Footer
    pdf.ln(5)
    pdf.set_font('helvetica', 'I', 9)
    pdf.cell(0, 5, 'Plan your perfect journey with Travel Advisor', 0, 1, 'C')
    
    # Save
    try:
        pdf.output(output_path)
        print(f"✅ PDF saved: {output_path}")
        return True
    except Exception as e:
        print(f"❌ PDF error: {e}")
        return False