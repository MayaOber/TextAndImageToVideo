from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import subprocess
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from dotenv import load_dotenv
import mimetypes
import pyshorteners
import cgi
import io
import urllib.parse
import threading
import uuid

load_dotenv(override=True)

# Store video generation tasks
video_tasks = {}

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type='text/html'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def shorten_url(self, url):
        try:
            s = pyshorteners.Shortener()
            return s.tinyurl.short(url)
        except Exception as e:
            print(f"Error shortening URL: {str(e)}")
            return url  # Return original URL if shortening fails

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        # Handle video status check
        if self.path.startswith('/check-video-status/'):
            try:
                task_id = self.path.split('/')[-1]
                if task_id in video_tasks:
                    self._set_headers(200, 'application/json')
                    self.wfile.write(json.dumps(video_tasks[task_id]).encode('utf-8'))
                    # Clean up completed tasks
                    if video_tasks[task_id].get('completed', False):
                        del video_tasks[task_id]
                    return
                else:
                    self._set_headers(404, 'application/json')
                    self.wfile.write(json.dumps({
                        'error': 'Task not found'
                    }).encode('utf-8'))
                    return
            except Exception as e:
                self._set_headers(500, 'application/json')
                self.wfile.write(json.dumps({
                    'error': str(e)
                }).encode('utf-8'))
                return

        # Regular file serving
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/.env':
            try:
                with open('.env', 'r', encoding='utf-8', errors='replace') as file:
                    content = file.read()
                    env_dict = {}
                    for line in content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith('#'):
                            try:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"\'')  # Remove quotes
                                env_dict[key] = value
                            except ValueError:
                                continue
                
                self._set_headers(200, 'application/json')
                self.wfile.write(json.dumps(env_dict).encode('utf-8'))
                return
            except Exception as e:
                print(f"Error reading .env file: {str(e)}")
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    'error': f'Error reading .env file: {str(e)}'
                }).encode('utf-8'))
                return
        
        try:
            # Parse URL and remove query parameters
            parsed_url = urllib.parse.urlparse(self.path)
            clean_path = parsed_url.path
            
            # Get the file path
            file_path = os.path.join(os.getcwd(), clean_path[1:])
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(file_path)
            if content_type is None:
                content_type = 'application/octet-stream'
            
            # Check if file is binary (images, etc.)
            is_binary = not (content_type.startswith('text/') or content_type in ['application/json', 'application/javascript'])
            
            # Open file in appropriate mode
            mode = 'rb' if is_binary else 'r'
            encoding = None if is_binary else 'utf-8'
            
            with open(file_path, mode=mode, encoding=encoding) as file:
                content = file.read()
            
            self._set_headers(200, content_type)
            if isinstance(content, str):
                self.wfile.write(content.encode('utf-8'))
            else:
                self.wfile.write(content)
                
        except Exception as e:
            print(f"Error serving file: {str(e)}")
            self._set_headers(404)
            self.wfile.write(b'404: File not found')

    def generate_video_async(self, task_id, form_data):
        try:
            print("\nExecuting generateVideo.py")  # Debug log
            script_path = os.path.abspath('generateVideo.py')
            process = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0:
                print(f"\nVideo generation failed: {process.stderr}")  # Debug log
                video_tasks[task_id] = {
                    'status': 'error',
                    'message': f'Video generation failed: {process.stderr}',
                    'completed': True
                }
                return
            
            print("\nVideo generation output:")  # Debug log
            print(process.stdout)  # Debug log
            
            # Extract video URL from the output
            output_lines = process.stdout.split('\n')
            video_url = None
            for line in output_lines:
                if line.startswith('video url:'):
                    video_url = line.replace('video url:', '').strip()
                    print(f"\nExtracted video URL: {video_url}")  # Debug log
                    break
            
            if video_url:
                # Shorten the video URL
                short_url = self.shorten_url(video_url)
                print(f"\nShortened video URL: {short_url}")  # Debug log

                print("\nAttempting to send email with video URL")  # Debug log
                # Send email with shortened video URL and form data
                email_success = self.send_email(
                    form_data['email'],
                    form_data['name'],
                    short_url,  # Use shortened URL in email
                    form_data.get('location'),
                    form_data.get('mobile')
                )
                
                video_tasks[task_id] = {
                    'status': 'success',
                    'videoUrl': short_url,
                    'completed': True,
                    'emailSent': email_success
                }
            else:
                video_tasks[task_id] = {
                    'status': 'error',
                    'message': 'Could not extract video URL from response',
                    'completed': True
                }
        except Exception as e:
            print(f"\nError in video generation: {str(e)}")  # Debug log
            video_tasks[task_id] = {
                'status': 'error',
                'message': str(e),
                'completed': True
            }

    def save_env_file(self, settings):
        env_content = f'''OPENAI_API_KEY="{settings['OPENAI_API_KEY']}"
ELEVENLABS_API_KEY="{settings['ELEVENLABS_API_KEY']}"
HEDRA_API_KEY="{settings['HEDRA_API_KEY']}"

STATIC_TEXT="{settings['STATIC_TEXT']}"

ELEVENLABS_VOICE_NAME="{settings['ELEVENLABS_VOICE_NAME']}"
ELEVENLABS_MODEL="{settings['ELEVENLABS_MODEL']}"

SMTP_SERVER={settings['SMTP_SERVER']}
SMTP_PORT={settings['SMTP_PORT']}
SMTP_USERNAME={settings['SMTP_USERNAME']}
SMTP_PASSWORD={settings['SMTP_PASSWORD']}
FROM_EMAIL={settings['FROM_EMAIL']}
CC_EMAIL={settings.get('CC_EMAIL', '')}'''
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)

    def save_file(self, fileitem, target_path):
        if fileitem.filename:
            with open(target_path, 'wb') as f:
                while True:
                    chunk = fileitem.file.read(100000)
                    if not chunk:
                        break
                    f.write(chunk)
            return True
        return False

    def send_email(self, to_email, name, video_url, location=None, mobile=None):
        print(f"\nAttempting to send email to {to_email}")  # Debug log
        try:
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_username = os.getenv('SMTP_USERNAME')
            smtp_password = os.getenv('SMTP_PASSWORD')
            from_email = os.getenv('FROM_EMAIL')
            cc_email = os.getenv('CC_EMAIL')

            if not all([smtp_username, smtp_password, from_email]):
                print("Email configuration missing")  # Debug log
                raise Exception("Email configuration missing")
           
            short_url = video_url
            print(f"Shortened URL for email: {short_url}")  # Debug log

            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            if cc_email:
                msg['Cc'] = cc_email
            msg['Subject'] = 'Your Personalized Video is Ready!'

            # Create a more personalized email body
            body = f"""
            Dear {name},

            Thank you for using our service! Your personalized video has been generated successfully.
            """

            # Add additional details if provided
            if location and mobile:
                body += f"""
                Your Details:
                - Name: {name}
                - Location: {location}
                - Mobile: {mobile}
                - Email: {to_email}
                """

            body += f"""
            You can view your personalized video at the following link:
            {short_url}

            We hope you enjoy your personalized video! Feel free to share it with your friends and family.

            Best regards,
            Your Company Name
            """

            msg.attach(MIMEText(body, 'plain'))

            print(f"Connecting to SMTP server: {smtp_server}:{smtp_port}")  # Debug log
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                print("Starting TLS")  # Debug log
                server.starttls()
                print("Logging in to SMTP server")  # Debug log
                server.login(smtp_username, smtp_password)
                print("Sending email")  # Debug log
                # Get all recipients including CC
                recipients = [to_email]
                if cc_email:
                    recipients.append(cc_email)
                server.send_message(msg)
                print("Email sent successfully!")  # Debug log

            return True
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False

    def do_POST(self):
        if self.path == '/save_settings':
            try:
                # Parse multipart form data
                content_type = self.headers.get('Content-Type')
                if not content_type or not content_type.startswith('multipart/form-data'):
                    raise ValueError("Expected multipart/form-data")

                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD': 'POST',
                            'CONTENT_TYPE': self.headers['Content-Type']}
                )

                # Get settings JSON
                settings = json.loads(form.getvalue('settings'))
                
                # Save settings to .env file
                self.save_env_file(settings)

                # Handle file uploads
                if 'audio' in form:
                    self.save_file(form['audio'], 'assets/audio.mp3')
                
                if 'image' in form:
                    self.save_file(form['image'], 'assets/image.jpg')

                self._set_headers(200, 'application/json')
                self.wfile.write(json.dumps({'status': 'success'}).encode('utf-8'))
                return

            except Exception as e:
                print(f"Error saving settings: {str(e)}")
                self._set_headers(500, 'application/json')
                self.wfile.write(json.dumps({
                    'status': 'error',
                    'message': str(e)
                }).encode('utf-8'))
                return

        elif self.path == '/generate-greeting':
            try:
                # Read the request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                name = data.get('name', '')

                print(f"Received request with name: {name}")  # Debug log

                # Ensure the assets directory exists
                os.makedirs('assets', exist_ok=True)

                # Get the absolute path to the Python script
                script_path = os.path.abspath('getAudioElevenLabs.py')
                print(f"Running script: {script_path} with name: {name}")  # Debug log

                # Run the ElevenLabs script with the name - without text=True
                result = subprocess.run(
                    [sys.executable, script_path, name],
                    check=True,
                    capture_output=True
                )
                
                # Safely decode output with error handling
                stdout = result.stdout.decode('utf-8', errors='replace')
                print(f"Script output: {stdout}")  # Debug log
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'status': 'success',
                    'output': stdout
                }).encode())
                
            except subprocess.CalledProcessError as e:
                stderr = e.stderr.decode('utf-8', errors='replace')
                print(f"Script error: {stderr}")  # Debug log
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': str(e),
                    'stderr': stderr
                }).encode())
            except Exception as e:
                print(f"Server error: {str(e)}")  # Debug log
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': str(e)
                }).encode())
                
        elif self.path == '/generate-video':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                if content_length > 0:
                    post_data = self.rfile.read(content_length)
                    form_data = json.loads(post_data.decode('utf-8'))
                    print(f"\nReceived form data for video generation: {form_data}")  # Debug log
                
                # Generate a unique task ID
                task_id = str(uuid.uuid4())
                
                # Initialize task status
                video_tasks[task_id] = {
                    'status': 'processing',
                    'completed': False
                }
                
                # Start video generation in a separate thread
                thread = threading.Thread(
                    target=self.generate_video_async,
                    args=(task_id, form_data)
                )
                thread.start()
                
                # Return task ID immediately
                self._set_headers(200, 'application/json')
                response = {
                    'status': 'processing',
                    'taskId': task_id,
                    'message': 'Video generation started'
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            
            except Exception as e:
                print(f"\nError in generate-video endpoint: {str(e)}")  # Debug log
                self._set_headers(500, 'application/json')
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))

        elif self.path == '/send-email':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))

                # Shorten the video URL for the email endpoint
                short_url = self.shorten_url(data['videoUrl'])
                
                if self.send_email(data['email'], data['name'], short_url):
                    self._set_headers(200, 'application/json')
                    response = {'status': 'success', 'message': 'Email sent successfully'}
                else:
                    self._set_headers(500, 'application/json')
                    response = {'status': 'error', 'message': 'Failed to send email'}
                
                self.wfile.write(json.dumps(response).encode('utf-8'))
            
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                self._set_headers(500, 'application/json')
                response = {'status': 'error', 'message': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self._set_headers(404)
            self.wfile.write(b'404: Endpoint not found')

def run_server(port=8000):
    # Get port from environment variable for Heroku
    port = int(os.environ.get('PORT', port))
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f'Server running on port {port}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down server...')
        httpd.server_close()

if __name__ == '__main__':
    run_server()
