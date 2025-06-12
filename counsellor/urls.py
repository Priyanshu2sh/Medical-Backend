from django.urls import path
from .views import CreateSessionAPI, CounsellorListView, CounsellorByCounsellorIdView,CounsellingRequestsByUserId, CounsellingRequestsByCounsellorId, UpdateRequestStatusAPI,CreatePrecautionAPIView,CreateTherapyStepsAPIView,FeedbackCreateView,TherapyStepsByUserView,FeedbackByCounsellorView,UpdateCurrentStepAPIView

urlpatterns = [
    path('counsellor-request/', CreateSessionAPI.as_view(), name='create-request'),
    path('counselling-requests/', CreateSessionAPI.as_view(), name='get-all-requests'),
    path('counsellors/', CounsellorListView.as_view(), name='counsellor-list'),
    path('counsellors/<int:counsellor_id>/', CounsellorByCounsellorIdView.as_view(), name='counsellor-detail'),
    path('counselling-requests/user/<int:user_id>/', CounsellingRequestsByUserId.as_view(), name='requests-by-user'),
    path('counselling-requests/counsellor/<int:counsellor_id>/', CounsellingRequestsByCounsellorId.as_view(), name='requests-by-counsellor-id'),
    path('counselling-request/update-status/<int:request_id>/', UpdateRequestStatusAPI.as_view(), name='update-request-status'),


    path('precautions/', CreatePrecautionAPIView.as_view(), name='create-precaution'),
    path('precaution/', CreatePrecautionAPIView.as_view(), name='precaution-list'),

    path('therapies/', CreateTherapyStepsAPIView.as_view(), name='create-therapy'),
    path('therapy-steps/', CreateTherapyStepsAPIView.as_view(), name='therapy-steps-list'),
    path('therapy/user/<int:user_id>/', TherapyStepsByUserView.as_view(), name='therapy-by-user'),
    path('therapy-steps/<int:pk>/update-current-step/', UpdateCurrentStepAPIView.as_view(), name='update-current-step'),

    path('feedback/', FeedbackCreateView.as_view(), name='create-feedback'),
    path('feedback-by-counsellor_id/<int:counsellor_id>/', FeedbackByCounsellorView.as_view(), name='feedback-by-counsellor'),

]