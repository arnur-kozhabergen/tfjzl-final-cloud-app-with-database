from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse
from .models import Course, Enrollment, Question, Choice, Submission


@override_settings(ALLOWED_HOSTS=['testserver'])
class AssessmentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='learner')
        self.other = User.objects.create_user(username='other')
        self.course = Course.objects.create(name='Learning Django', description='Test course')
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.question = Question.objects.create(course=self.course, content='Select Python frameworks', grade=100)
        self.yes = Choice.objects.create(question=self.question, content='Django', is_correct=True)
        self.yes2 = Choice.objects.create(question=self.question, content='Flask', is_correct=True)
        self.no = Choice.objects.create(question=self.question, content='Spring')
        self.submit_url = reverse('onlinecourse:submit', args=[self.course.id])

    def test_exact_multiselect_scoring(self):
        self.assertTrue(self.question.is_get_score([self.yes.id, self.yes2.id]))
        self.assertFalse(self.question.is_get_score([self.yes.id]))
        self.assertFalse(self.question.is_get_score([self.yes.id, self.yes2.id, self.no.id]))
        self.assertFalse(self.question.is_get_score([]))

    def test_successful_submission_and_rendered_feedback(self):
        self.client.force_login(self.user)
        response = self.client.post(self.submit_url, {'choice_1': self.yes.id, 'choice_2': self.yes2.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Congratulations')
        self.assertEqual(response.context['grade'], 100)
        self.assertEqual(Submission.objects.get().choices.count(), 2)

    def test_wrong_choice_fails_and_offers_retest(self):
        self.client.force_login(self.user)
        response = self.client.post(self.submit_url, {'choice_1': self.no.id}, follow=True)
        self.assertEqual(response.context['grade'], 0)
        self.assertContains(response, 'Re-test')
        self.assertContains(response, 'Your selection')

    def test_requires_login_enrollment_and_post(self):
        self.assertEqual(self.client.post(self.submit_url).status_code, 302)
        self.client.force_login(self.other)
        self.assertEqual(self.client.post(self.submit_url).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.submit_url).status_code, 405)
        self.assertEqual(Submission.objects.count(), 0)

    def test_result_only_visible_to_owner_and_correct_course(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        result_url = reverse('onlinecourse:show_exam_result', args=[self.course.id, submission.id])
        self.client.force_login(self.other)
        self.assertEqual(self.client.get(result_url).status_code, 404)
        self.client.force_login(self.user)
        wrong_course = Course.objects.create(name='Another course')
        wrong_url = reverse('onlinecourse:show_exam_result', args=[wrong_course.id, submission.id])
        self.assertEqual(self.client.get(wrong_url).status_code, 404)

    def test_foreign_course_choices_are_not_saved(self):
        other_course = Course.objects.create(name='Other')
        other_question = Question.objects.create(course=other_course, content='Foreign question')
        foreign_choice = Choice.objects.create(question=other_question, content='Foreign', is_correct=True)
        self.client.force_login(self.user)
        self.client.post(self.submit_url, {'choice_1': foreign_choice.id, 'choice_bad': 'invalid'})
        self.assertEqual(Submission.objects.get().choices.count(), 0)

    def test_detail_template_compiles_and_contains_exam(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('onlinecourse:course_details', args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Start Exam')
        self.assertContains(response, 'Select Python frameworks')

    def test_unenrolled_detail_offers_enrollment_instead_of_exam(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse('onlinecourse:course_details', args=[self.course.id]))
        self.assertContains(response, 'Enroll to take the exam')
        self.assertNotContains(response, 'Start Exam')
