from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
import backend

# Set window size
Window.size = (600, 800)

class LoginSignupScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginSignupScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # Create login and signup buttons first
        login_button = Button(text='Login', size_hint_y=None, height=50)
        login_button.bind(on_press=self.show_login_fields)

        signup_button = Button(text='Sign Up', size_hint_y=None, height=50)
        signup_button.bind(on_press=self.show_signup_fields)

        # Add these buttons to the layout first
        self.layout.add_widget(login_button)
        self.layout.add_widget(signup_button)

        # Create username and password fields but don't add them yet
        self.username_input = TextInput(hint_text='Username', size_hint_y=None, height=50)
        self.password_input = TextInput(hint_text='Password', password=True, size_hint_y=None, height=50)

        # Submit button (for either login or signup)
        self.submit_button = Button(text='Submit', size_hint_y=None, height=50)
        self.submit_button.bind(on_press=self.process_login_signup)

        # Back button to go back to login/signup selection screen
        self.back_button = Button(text='Back', size_hint_y=None, height=50)
        self.back_button.bind(on_press=self.go_back)

        # Add the layout to the screen
        self.add_widget(self.layout)

        # Flag to keep track of current mode (login or signup)
        self.mode = None

        # To track the logged-in user
        self.current_user_id = None

    def show_login_fields(self, instance):
        self.mode = 'login'
        self.update_ui_for_login_signup()

    def show_signup_fields(self, instance):
        self.mode = 'signup'
        self.update_ui_for_login_signup()

    def update_ui_for_login_signup(self):
        # Clear the layout and only show username, password, submit button, and back button
        self.layout.clear_widgets()

        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)
        self.submit_button.text = 'Login' if self.mode == 'login' else 'Sign Up'
        self.layout.add_widget(self.submit_button)
        self.layout.add_widget(self.back_button)

    def process_login_signup(self, instance):
        username = self.username_input.text
        password = self.password_input.text

        if self.mode == 'login':
            user_id = backend.login(username, password)
            if user_id:
                self.current_user_id = user_id  # Save user ID upon successful login
                self.show_feedback_popup("Login Successful!", "You have logged in successfully.")
                self.manager.current = 'main'  # Switch to MainScreen on successful login
            else:
                self.show_feedback_popup("Login Failed", "Invalid credentials. Please try again.")
        elif self.mode == 'signup':
            if backend.signup(username, password):
                self.show_feedback_popup("Signup Successful!", "You can now log in.")
                self.username_input.text = ''
                self.password_input.text = ''  # Clear inputs after signup
                self.manager.current = 'login_signup'  # Redirect to login after signup
            else:
                self.show_feedback_popup("Signup Failed", "Username already exists. Please try another.")

    def go_back(self, instance):
        # Go back to the login/signup selection screen
        self.layout.clear_widgets()
        self.layout.add_widget(Button(text='Login', size_hint_y=None, height=50, on_press=self.show_login_fields))
        self.layout.add_widget(Button(text='Sign Up', size_hint_y=None, height=50, on_press=self.show_signup_fields))

    def show_feedback_popup(self, title, message):
        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text=message))

        close_button = Button(text='Close', size_hint_y=None, height=50)
        close_button.bind(on_press=lambda instance: popup.dismiss())
        content.add_widget(close_button)

        popup = Popup(title=title, content=content, size_hint=(0.6, 0.4))
        popup.open()


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        # Add note button
        add_note_button = Button(text='Add Note', size_hint_y=None, height=50)
        add_note_button.bind(on_press=self.switch_to_add_note)
        self.layout.add_widget(add_note_button)

        # Show notes button
        show_notes_button = Button(text='Show Notes', size_hint_y=None, height=50)
        show_notes_button.bind(on_press=self.show_notes)
        self.layout.add_widget(show_notes_button)

        # ScrollView to hold all notes
        self.notes_container = GridLayout(cols=1, size_hint_y=None)
        self.notes_container.bind(minimum_height=self.notes_container.setter('height'))  # Dynamically adjust height
        scroll_view = ScrollView(size_hint=(1, 0.8))
        scroll_view.add_widget(self.notes_container)

        self.layout.add_widget(scroll_view)
        self.add_widget(self.layout)

        # To keep track of the logged-in user
        self.current_user_id = None

    def switch_to_add_note(self, instance):
        self.manager.current = 'add_note'

    def show_notes(self, instance):
        self.notes_container.clear_widgets()
        notes = backend.retrieve_data(self.manager.get_screen('login_signup').current_user_id)  # Get user ID from LoginSignupScreen
        if notes:
            for note in notes:
                note_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=70)

                note_button = Button(text=note[1], size_hint_x=0.6)
                note_button.bind(on_press=lambda btn, note_id=note[0]: self.show_note_detail(note_id))

                update_button = Button(text='Update', size_hint_x=0.2)
                update_button.bind(on_press=lambda btn, note_id=note[0]: self.update_note_details(note_id))

                delete_button = Button(text='Delete', size_hint_x=0.2)
                delete_button.bind(on_press=lambda btn, note_id=note[0]: self.delete_note_confirmation(note_id))

                note_layout.add_widget(note_button)
                note_layout.add_widget(update_button)
                note_layout.add_widget(delete_button)

                modified_time_label = Label(text=f"Last Modified: {note[3]}", size_hint_x=1)
                note_layout.add_widget(modified_time_label)  # Show modified time below the note

                self.notes_container.add_widget(note_layout)

        else:
            # Show a message if no notes are found
            self.notes_container.add_widget(Label(text="No notes available.", size_hint_y=None, height=50))

    def show_note_detail(self, note_id):
        self.manager.get_screen('note_detail').load_note_details(note_id)
        self.manager.current = 'note_detail'

    def update_note_details(self, note_id):
        self.manager.get_screen('note_detail').load_note_details(note_id)
        self.manager.current = 'note_detail'

    def delete_note_confirmation(self, note_id):
        content = BoxLayout(orientation='vertical')

        backup_button = Button(text='Backup and Delete')
        delete_button = Button(text='Delete Without Backup')
        cancel_button = Button(text='Cancel')

        content.add_widget(backup_button)
        content.add_widget(delete_button)
        content.add_widget(cancel_button)

        popup = Popup(title='Confirm Deletion', content=content, size_hint=(0.6, 0.4))

        def backup_and_delete(instance):
            # Backup the note
            backup_filename = backend.backup_note_to_file(note_id)
            if backup_filename:
                print(f"Note backed up at {backup_filename}")
            # Delete the note
            backend.delete_data(note_id)
            self.show_notes(instance)  # Refresh the notes
            popup.dismiss()

        backup_button.bind(on_press=backup_and_delete)
        delete_button.bind(on_press=lambda instance: [backend.delete_data(note_id), self.show_notes(instance), popup.dismiss()])
        cancel_button.bind(on_press=popup.dismiss)

        popup.open()
class NoteDetailScreen(Screen):
    def __init__(self, **kwargs):
        super(NoteDetailScreen, self).__init__(**kwargs)

        layout = BoxLayout(orientation='vertical')

        # Input fields for note details
        self.title_input = TextInput(hint_text='Note Title', size_hint_y=None, height=50)
        self.content_input = TextInput(hint_text='Note Content', size_hint_y=None, height=400, multiline=True)

        # Save button
        save_button = Button(text='Save', size_hint_y=None, height=50)
        save_button.bind(on_press=self.save_note)

        # Add widgets to layout
        layout.add_widget(self.title_input)
        layout.add_widget(self.content_input)
        layout.add_widget(save_button)

        self.add_widget(layout)

    def load_note_details(self, note_id):
        note = backend.get_note_by_id(note_id)
        if note:
            self.title_input.text = note[1]
            self.content_input.text = note[2]
            self.note_id = note[0]  # Save the note ID for updating

    def save_note(self, instance):
        note_title = self.title_input.text
        note_content = self.content_input.text
        if note_title and note_content:
            backend.update_data(note_title, note_content, self.note_id)  # Update using both title and content
            self.manager.current = 'main'
        else:
            self.show_error_popup()

    def show_error_popup(self):
        popup = Popup(title='Error', content=Label(text="Title and content cannot be empty"), size_hint=(0.6, 0.4))
        popup.open()




class AddNoteScreen(Screen):
    def __init__(self, **kwargs):
        super(AddNoteScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')

        self.title_input = TextInput(hint_text='Title', size_hint_y=None, height=50)
        self.content_input = TextInput(hint_text='Content', size_hint_y=None, height=400)

        add_note_button = Button(text='Add Note', size_hint_y=None, height=50)
        add_note_button.bind(on_press=self.add_note)

        self.layout.add_widget(self.title_input)
        self.layout.add_widget(self.content_input)
        self.layout.add_widget(add_note_button)

        self.add_widget(self.layout)

    def add_note(self, instance):
        title = self.title_input.text
        content = self.content_input.text
        user_id = self.manager.get_screen('login_signup').current_user_id  # Get the user ID from the previous screen

        if title and content:
            backend.insert_data(title, content, user_id)  # Pass user ID to insert
            self.title_input.text = ''
            self.content_input.text = ''
            self.manager.current = 'main'
            self.manager.get_screen('main').show_notes(instance)  # Refresh notes after adding a new one


class MyApp(App):
    def build(self):
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LoginSignupScreen(name='login_signup'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AddNoteScreen(name='add_note'))
        sm.add_widget(NoteDetailScreen(name='note_detail'))
        return sm


if __name__ == '__main__':
    MyApp().run()
