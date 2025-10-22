import subprocess, urllib.parse, webbrowser
from tkinter import messagebox

def open_email_mac_mail(recipient, subject, body):
    script = f'''
    tell application "Mail"
        set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}", visible:true}}
        tell newMessage
            make new to recipient at end of to recipients with properties {{address:"{recipient}"}}
        end tell
        activate
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception:
        try:
            mailto = f"mailto:{recipient}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
            webbrowser.open(mailto)
        except Exception as e:
            messagebox.showerror("Email Error", f"Could not open email client.\n{e}")

def confirm_delete():
    return messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?")
