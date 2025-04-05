from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework import serializers
from rest_framework import status
import requests
from .utils import extract_text_from_pdf, extract_skills,extract_experience  # Import your functions
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Resume, Job
import spacy
import logging
import tempfile
logger = logging.getLogger(__name__)  # Enable logging

# Serializer for the sign-up form
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
    
    # Print and log errors
    logger.warning(f"Signup validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


nlp = spacy.load("en_core_web_sm")
# View for logging in and receiving a JWT token
@api_view(["POST"])
@permission_classes([AllowAny])  # This makes it accessible to all users
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)  # Authenticate user
    if user is not None:
        # Generate JWT Token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return Response({"access_token": access_token, "refresh_token": str(refresh)}, status=200)
    else:
        return Response({"error": "Invalid credentials"}, status=401)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_resume(request):
    file = request.FILES.get("resume")
    
    if not file:
        return Response({"error": "No file uploaded"}, status=400)

    # Use tempfile to create a temporary file in a cross-platform manner
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        pdf_path = temp_file.name  # This provides a safe temporary file path
        with open(pdf_path, "wb") as f:
            f.write(file.read())

    # Extract text from the uploaded resume
    resume_text = extract_text_from_pdf(pdf_path)

    if not resume_text:
        return Response({"error": "Unable to extract text from the resume"}, status=400)

    # Extract skills and experience from the resume text
    skills = extract_skills(resume_text)
    experience = extract_experience(resume_text)

    # Save the resume to the database
    Resume.objects.create(user=request.user, file=file, skills=skills, experience=experience)

    # Return the extracted text and save status in the required format
    return Response({
        "resume_text": resume_text,
    })


# FastAPI endpoint URL
FASTAPI_URL = 'http://localhost:8000/recommend/'  # Adjust if needed

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_recommended_jobs(request):
    # Fetch the user's resume text from the request (you might have it stored or passed in the query parameters)
    resume_text = request.query_params.get('resume_text', None)

    # Check if the resume text is provided
    if not resume_text:
        return Response({"error": "No resume text provided"}, status=400)

    # Send a POST request to the FastAPI recommendation API
    try:
        response = requests.post(FASTAPI_URL, json={"resume_text": resume_text})
        
        # Check if the response is successful
        if response.status_code == 200:
            recommended_jobs = response.json()["recommended_jobs"]
            return Response(recommended_jobs)
        else:
            return Response({"error": "Failed to get recommendations from FastAPI"}, status=500)
    except requests.exceptions.RequestException as e:
        return Response({"error": f"Error calling FastAPI: {str(e)}"}, status=500)


