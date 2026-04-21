from flask import Flask, render_template, jsonify, request, session
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'

# ============================================================
# USSD MENUS (Same structure as HTML version)
# ============================================================
MENUS = {
    "main": {
        "text": "1. Ikali - Data and Voice\n2. Airtel SoChe Pack\n3. All networks Soche\n4. Data Packs\n5. Buy for Other\n6. Balance Check\n7. Siliza-Airtime Loan\n8. Get Airtel App (1GB Free)\n9. INTL calling & roaming",
        "hasInput": True,
        "inputPlaceholder": "Enter option (1-9)",
        "options": {
            "1": "menu_ikali",
            "2": "menu_soche",
            "3": "menu_allnet",
            "4": "menu_data",
            "5": "menu_buyother",
            "6": "action_balance",
            "7": "menu_siliza",
            "8": "action_getapp",
            "9": "menu_intl",
        }
    },
    
    "menu_ikali": {
        "text": "1. For 24hours Daily Pack\n2. For Weekly Pack\n3. For Monthly Pack\n4. Buy for Other\n5. Cancel Auto Renewal\n0. Return to main menu",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "main",
        "options": {
            "1": "menu_ikali_daily",
            "2": "menu_ikali_weekly",
            "3": "menu_ikali_monthly",
            "4": "menu_buyother_ikali",
            "5": "action_cancel_renewal",
            "0": "main",
        }
    },
    
    "menu_ikali_daily": {
        "text": "Select:\n1. K2 = 7 Airtel Min, 26Hrs\n2. K5 = 32 Airtel Min, 24Hrs\n3. K10 = 52 Mins Onnet, 7Days\n4. K5 = 250MB, 24hrs\n5. K10 = 600MB, 7Days\n6. K20 = 1.5GB, 7Days\n7. K99 = 10GB, 30Days",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "menu_ikali",
        "options": {
            "1": {"action": "purchase", "msg": "K2 - 7 Airtel Minutes, 26 Hours. Your purchase was successful!"},
            "2": {"action": "purchase", "msg": "K5 - 32 Airtel Minutes, 24 Hours. Your purchase was successful!"},
            "3": {"action": "purchase", "msg": "K10 - 52 Mins Onnet, 7 Days. Your purchase was successful!"},
            "4": {"action": "purchase", "msg": "K5 - 250MB, 24 Hours. Your purchase was successful!"},
            "5": {"action": "purchase", "msg": "K10 - 600MB, 7 Days. Your purchase was successful!"},
            "6": {"action": "purchase", "msg": "K20 - 1.5GB, 7 Days. Your purchase was successful!"},
            "7": {"action": "purchase", "msg": "K99 - 10GB, 30 Days. Your purchase was successful!"},
        }
    },
    
    "menu_ikali_weekly": {
        "text": "Select Weekly Pack:\n1. K10 = 600MB, 7Days\n2. K20 = 1.5GB, 7Days\n3. K50 = 5GB, 7Days\n4. K99 = 10GB, 7Days",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "menu_ikali",
        "options": {
            "1": {"action": "purchase", "msg": "K10 - 600MB, 7 Days. Your purchase was successful!"},
            "2": {"action": "purchase", "msg": "K20 - 1.5GB, 7 Days. Your purchase was successful!"},
            "3": {"action": "purchase", "msg": "K50 - 5GB, 7 Days. Your purchase was successful!"},
            "4": {"action": "purchase", "msg": "K99 - 10GB, 7 Days. Your purchase was successful!"},
        }
    },
    
    "menu_ikali_monthly": {
        "text": "Select Monthly Pack:\n1. K50 = 5GB, 30Days\n2. K99 = 10GB, 30Days\n3. K150 = 20GB, 30Days\n4. K299 = 50GB, 30Days",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "menu_ikali",
        "options": {
            "1": {"action": "purchase", "msg": "K50 - 5GB, 30 Days. Your purchase was successful!"},
            "2": {"action": "purchase", "msg": "K99 - 10GB, 30 Days. Your purchase was successful!"},
            "3": {"action": "purchase", "msg": "K150 - 20GB, 30 Days. Your purchase was successful!"},
            "4": {"action": "purchase", "msg": "K299 - 50GB, 30 Days. Your purchase was successful!"},
        }
    },
    
    "menu_soche": {
        "text": "Airtel SoChe Pack:\n1. For 24hours Daily Pack\n2. For Weekly Pack\n3. For Monthly Pack\n4. Buy for Other\n5. Cancel Auto Renewal\n0. Return to main menu",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "main",
        "options": {
            "1": "menu_soche_daily",
            "2": "menu_soche_weekly",
            "3": "menu_soche_monthly",
            "4": "menu_buyother",
            "5": "action_cancel_renewal",
            "0": "main",
        }
    },
    
    "menu_soche_daily": {
        "text": "SoChe Daily:\n1. K2 = WhatsApp 24hrs\n2. K5 = Social 24hrs\n3. K10 = Social+YouTube 24hrs",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "menu_soche",
        "options": {
            "1": {"action": "purchase", "msg": "K2 WhatsApp 24hrs pack activated! Enjoy WhatsApp for 24 hours."},
            "2": {"action": "purchase", "msg": "K5 Social 24hrs pack activated! Enjoy Facebook, Twitter & Instagram."},
            "3": {"action": "purchase", "msg": "K10 Social+YouTube 24hrs activated! Enjoy social media and YouTube."},
        }
    },
    
    "menu_soche_weekly": {
        "text": "SoChe Weekly:\n1. K5 = Social 7Days\n2. K15 = Social+YouTube 7Days",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "menu_soche",
        "options": {
            "1": {"action": "purchase", "msg": "K5 Social 7-Day pack activated! Enjoy social media for 7 days."},
            "2": {"action": "purchase", "msg": "K15 Social+YouTube 7-Day pack activated!"},
        }
    },
    
    "menu_soche_monthly": {
        "text": "SoChe Monthly:\n1. K20 = Social 30Days\n2. K50 = Social+YouTube 30Days",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "menu_soche",
        "options": {
            "1": {"action": "purchase", "msg": "K20 Social 30-Day pack activated!"},
            "2": {"action": "purchase", "msg": "K50 Social+YouTube 30-Day pack activated!"},
        }
    },
    
    "menu_allnet": {
        "text": "All Networks Soche:\n1. Ikali - Data and Voice\n2. Tonse Internet Bundles\n3. Buy for other\n4. Check balance\n5. Night Data\n6. Cancel auto renewal",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "main",
        "options": {
            "1": "menu_ikali",
            "2": "menu_tonse",
            "3": "menu_buyother",
            "4": "action_balance",
            "5": "menu_nightdata",
            "6": "action_cancel_renewal",
            "0": "main",
        }
    },
    
    "menu_tonse": {
        "text": "Tonse Internet Bundles:\n1. K10 = 600MB, 7Days\n2. K20 = 1.5GB, 7Days\n3. K50 = 5GB, 30Days\n4. K99 = 10GB, 30Days",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "menu_allnet",
        "options": {
            "1": {"action": "purchase", "msg": "K10 Tonse 600MB, 7 Days activated!"},
            "2": {"action": "purchase", "msg": "K20 Tonse 1.5GB, 7 Days activated!"},
            "3": {"action": "purchase", "msg": "K50 Tonse 5GB, 30 Days activated!"},
            "4": {"action": "purchase", "msg": "K99 Tonse 10GB, 30 Days activated!"},
        }
    },
    
    "menu_nightdata": {
        "text": "Night Data (12am - 5am):\n1. K5 = 1GB Night, 7Days\n2. K10 = 3GB Night, 7Days\n3. K20 = 5GB Night, 30Days",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "menu_allnet",
        "options": {
            "1": {"action": "purchase", "msg": "K5 Night Data 1GB (7 Days) activated! Valid 12am-5am daily."},
            "2": {"action": "purchase", "msg": "K10 Night Data 3GB (7 Days) activated! Valid 12am-5am daily."},
            "3": {"action": "purchase", "msg": "K20 Night Data 5GB (30 Days) activated! Valid 12am-5am daily."},
        }
    },
    
    "menu_data": {
        "text": "Data Packs:\n1. For 24hours Daily Pack\n2. For Weekly Pack\n3. For Monthly Pack\n4. Buy for Other\n0. Return to main menu",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "main",
        "options": {
            "1": "menu_ikali_daily",
            "2": "menu_ikali_weekly",
            "3": "menu_ikali_monthly",
            "4": "menu_buyother",
            "0": "main",
        }
    },
    
    "menu_buyother": {
        "text": "Please enter the subscriber's number you wish to purchase a bundle for\n(097xxxxxxx / 077xxxxxxx / 057xxxxxxx)",
        "hasInput": True,
        "inputPlaceholder": "Enter phone number",
        "parent": "main",
        "phoneInput": True,
        "options": {}
    },
    
    "menu_buyother_ikali": {
        "text": "Please enter the subscriber's number you wish to purchase a bundle for\n(097xxxxxxx / 077xxxxxxx / 057xxxxxxx)",
        "hasInput": True,
        "inputPlaceholder": "Enter phone number",
        "parent": "menu_ikali",
        "phoneInput": True,
        "options": {}
    },
    
    "menu_siliza": {
        "text": "Reply with:\n\n1 for Siliza Airtime\n2 for Eligibility Check\n3 for Payment\n4 for Help\n5 for Balance Check",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "main",
        "options": {
            "1": {"action": "msg", "msg": "Dear Customer, you have borrowed K10 airtime. You will be charged K11 on your next recharge. Thank you for using Siliza!"},
            "2": {"action": "msg", "msg": "Dear Customer, you are eligible to borrow up to K20 airtime via Siliza. Dial *117# > 7 to borrow."},
            "3": {"action": "msg", "msg": "Dear Customer, your Siliza balance of K0.00 has been cleared. Thank you!"},
            "4": {"action": "msg", "msg": "Siliza Airtime Loan allows you to borrow airtime when your balance is low. You repay on your next recharge. For help call 111."},
            "5": {"action": "msg", "msg": "Dear Customer, your Siliza outstanding balance is K0.00. Thank you!"},
            "0": "main",
        }
    },
    
    "menu_intl": {
        "text": "9. INTL calling & roaming\n0. Return to main menu",
        "hasInput": True,
        "inputPlaceholder": "Enter option",
        "parent": "main",
        "options": {
            "9": {"action": "msg", "msg": "International Calling Rates:\nSouth Africa: K2.50/min\nUK: K3.00/min\nUSA: K3.50/min\nZimbabwe: K2.00/min\nFor roaming packages dial *117# > 9."},
            "0": "main",
        }
    },
}

# Special actions handler
def handle_special_action(action):
    actions = {
        "action_balance": "Dear Customer, your balance request is being processed. You will receive a confirmation message shortly.",
        "action_cancel_renewal": "Dear Customer, your Auto Renewal has been cancelled successfully. You will not be automatically renewed for any bundle.",
        "action_getapp": "Dear Customer, your request is being processed. You will receive a confirmation message with a link shortly. Click the link to download the App."
    }
    return actions.get(action, "Action processed successfully.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/time', methods=['GET'])
def get_time():
    now = datetime.now()
    return jsonify({
        'time': now.strftime('%H:%M'),
        'date': now.strftime('%A, %B %d')
    })

@app.route('/api/ussd/menu/<menu_key>', methods=['GET'])
def get_menu(menu_key):
    if menu_key in MENUS:
        menu = MENUS[menu_key].copy()
        # Don't send options to client for security
        if 'options' in menu:
            del menu['options']
        return jsonify(menu)
    return jsonify({'error': 'Menu not found'}), 404

@app.route('/api/ussd/submit', methods=['POST'])
def submit_ussd():
    data = request.json
    menu_key = data.get('menu')
    user_input = data.get('input', '').strip()
    
    if not menu_key or menu_key not in MENUS:
        return jsonify({'error': 'Invalid menu'}), 400
    
    menu = MENUS[menu_key]
    
    # Handle phone number input
    if menu.get('phoneInput'):
        digits = ''.join(c for c in user_input if c.isdigit())
        if len(digits) >= 9:
            return jsonify({
                'action': 'message',
                'message': f"Dear Customer, you have successfully requested a bundle purchase for {user_input}. The bundle will be activated shortly."
            })
        else:
            return jsonify({'error': 'Invalid phone number'}), 400
    
    # Handle special actions
    if menu_key.startswith('action_'):
        return jsonify({
            'action': 'message',
            'message': handle_special_action(menu_key)
        })
    
    # Get option
    option = menu.get('options', {}).get(user_input)
    
    if not option:
        # Check for return to parent
        if user_input == '0' and menu.get('parent'):
            return jsonify({'action': 'menu', 'menu': menu['parent']})
        return jsonify({'error': 'Invalid option'}), 400
    
    # Handle string option (menu navigation or action)
    if isinstance(option, str):
        if option.startswith('action_'):
            return jsonify({
                'action': 'message',
                'message': handle_special_action(option)
            })
        else:
            return jsonify({'action': 'menu', 'menu': option})
    
    # Handle object option (purchase or message)
    if isinstance(option, dict):
        return jsonify({
            'action': 'message',
            'message': f"Dear Customer,\n{option['msg']}"
        })
    
    return jsonify({'error': 'Invalid menu configuration'}), 500

@app.route('/api/messages', methods=['GET'])
def get_messages():
    if 'messages' not in session:
        session['messages'] = []
    return jsonify(session.get('messages', []))

@app.route('/api/messages', methods=['POST'])
def add_message():
    data = request.json
    sender = data.get('sender', 'Airtel')
    text = data.get('text', '')
    
    if 'messages' not in session:
        session['messages'] = []
    
    messages = session['messages']
    now = datetime.now()
    time_str = now.strftime('%H:%M')
    
    # Check if sender exists
    existing = next((m for m in messages if m['sender'] == sender), None)
    
    if existing:
        existing['preview'] = text.split('\n')[-1][:50]
        existing['time'] = time_str
        existing['bubbles'].append({'text': text, 'time': time_str})
    else:
        messages.insert(0, {
            'sender': sender,
            'preview': text.split('\n')[-1][:50],
            'time': time_str,
            'bubbles': [{'text': text, 'time': time_str}]
        })
    
    session['messages'] = messages
    session['unread'] = session.get('unread', 0) + 1
    
    return jsonify({'success': True})

@app.route('/api/messages/read', methods=['POST'])
def mark_messages_read():
    session['unread'] = 0
    return jsonify({'success': True})

@app.route('/api/unread', methods=['GET'])
def get_unread():
    return jsonify({'unread': session.get('unread', 0)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
