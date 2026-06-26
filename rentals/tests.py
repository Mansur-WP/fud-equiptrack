from django.test import TestCase
from django.contrib.auth import get_user_model
from equipment.models import Equipment
from rentals.models import RentalRequest, Rental
from rentals.services import issue_equipment, InvalidRentalRequestError, RequestAlreadyIssuedError, EquipmentUnavailableError

User = get_user_model()

class IssuanceTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser("admin", "admin@test.com", "password")
        self.student = User.objects.create_user("student", "student@test.com", "password", role=User.Role.STUDENT)
        self.equipment = Equipment.objects.create(
            name="Laptop",
            serial_number="LT-001",
            quantity=5,
            available_quantity=5,
            status=Equipment.Status.AVAILABLE
        )
        self.rental_request = RentalRequest.objects.create(
            requester=self.student,
            equipment=self.equipment,
            quantity=2,
            purpose="Project",
            request_date="2026-06-25",
            expected_return_date="2026-07-01",
            status=RentalRequest.Status.APPROVED
        )

    def test_successful_issuance(self):
        rental = issue_equipment(self.rental_request, self.admin_user, "Here you go")
        self.assertEqual(rental.equipment, self.equipment)
        self.assertEqual(rental.issued_to, self.student)
        self.assertEqual(rental.issued_by, self.admin_user)
        self.assertEqual(rental.quantity, 2)
        
        # Verify stock deduction
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.available_quantity, 3)

    def test_duplicate_issuance(self):
        issue_equipment(self.rental_request, self.admin_user, "First issue")
        with self.assertRaises(RequestAlreadyIssuedError):
            issue_equipment(self.rental_request, self.admin_user, "Second issue")

    def test_invalid_request_state(self):
        self.rental_request.status = RentalRequest.Status.PENDING
        self.rental_request.save()
        with self.assertRaises(InvalidRentalRequestError):
            issue_equipment(self.rental_request, self.admin_user, "Pending issue")

    def test_stock_deduction_and_unavailable(self):
        # Request more than available
        self.rental_request.quantity = 10
        self.rental_request.save()
        with self.assertRaises(EquipmentUnavailableError):
            issue_equipment(self.rental_request, self.admin_user, "Over stock")


from django.urls import reverse

class RentalViewTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin_v", "admin@v.com", "pass")
        self.student = User.objects.create_user("student_v", "student@v.com", "pass", role=User.Role.STUDENT)
        self.student2 = User.objects.create_user("student2_v", "student2@v.com", "pass", role=User.Role.STUDENT)
        
        self.equipment = Equipment.objects.create(name="E1", serial_number="S1", quantity=10, available_quantity=10)
        
        self.req1 = RentalRequest.objects.create(requester=self.student, equipment=self.equipment, request_date="2026-06-25", expected_return_date="2026-07-01", status=RentalRequest.Status.APPROVED)
        self.req2 = RentalRequest.objects.create(requester=self.student2, equipment=self.equipment, request_date="2026-06-25", expected_return_date="2026-07-01", status=RentalRequest.Status.APPROVED)
        
        self.rental1 = issue_equipment(self.req1, self.admin)
        self.rental2 = issue_equipment(self.req2, self.admin)

    def test_list_view_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("rentals:active_rentals"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["rentals"]), 2)

    def test_list_view_student(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("rentals:active_rentals"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["rentals"]), 1)
        self.assertEqual(response.context["rentals"][0], self.rental1)

    def test_detail_view_student_own(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("rentals:rental_detail", args=[self.rental1.pk]))
        self.assertEqual(response.status_code, 200)

    def test_detail_view_student_other(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("rentals:rental_detail", args=[self.rental2.pk]))
        self.assertEqual(response.status_code, 404)

