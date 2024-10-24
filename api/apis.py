import random
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import EmailVerificationToken
from .serializers import UserSerializer
from .tasks import send_verification_email, send_winner_notification


User = get_user_model()


@api_view(['POST'])
def check_email(request):
    email = request.data.get('email')
    exists = User.objects.filter(email=email).exists()
    return Response({'exists': exists}, status=status.HTTP_200_OK)


@api_view(['POST'])
def register(request):
    email = request.data.get('email')
    if User.objects.filter(email=email).exists():
        return Response({'message': 'El correo electrónico ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        verification_token = str(uuid.uuid4())
        EmailVerificationToken.objects.create(user=user, token=verification_token)

        verification_link = f"{settings.FRONTEND_URL}?token={verification_token}&email={user.email}"
        try:
            send_verification_email.delay(verification_link, user.email)
            return Response({'message': 'Revise su correo para completar su registro'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Fallo al enviar correo de verificación: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def verify_email(request):
    token = request.GET.get('token')
    email = request.GET.get('email')

    try:
        verification_record = EmailVerificationToken.objects.get(token=token, user__email=email)

        if verification_record.is_expired():
            return Response({'error': 'This token has expired.'}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = verification_record.user
        user.set_password(password)
        user.save()
        verification_record.delete()

        return Response({'message': 'Your email has been verified and your password has been set.'}, status=status.HTTP_200_OK)

    except EmailVerificationToken.DoesNotExist:
        return Response({'error': 'Invalid token or email.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    try:
        user = get_object_or_404(User, email=request.data['email'])
    except Http404:
        return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
    
    if not user.check_password(request.data['password']):
        return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)

    return Response({
        'token': token.key,
        'user': serializer.data,
        'is_staff': user.is_staff
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(f'Hello {request.user.first_name}', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_view(request):
    return Response({'message': 'Esta es la vista de administración.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def generate_winner(request):
    active_users = User.objects.filter(is_active=True, is_staff=False)

    if not active_users.exists():
        return Response({'error': 'No hay usuarios activos registrados.'}, status=400)

    winner = random.choice(active_users)

    if winner:
        send_winner_notification.delay(winner.first_name, winner.last_name, winner.email)

    serializer = UserSerializer(winner)

    return Response({'Ganador': serializer.data}, status=200)
