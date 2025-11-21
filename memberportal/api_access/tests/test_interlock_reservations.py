from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from access.models import Interlock, InterlockReservation
from profile.models import Profile


User = get_user_model()


class InterlockReservationOverviewTests(APITestCase):
    def setUp(self):
        self.now = timezone.now()
        self.user = User.objects.create_user(
            email="member@example.com", password="password"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            screen_name="member",
            first_name="Test",
            last_name="User",
            phone="0412345678",
            state="active",
        )

        self.interlock = Interlock.objects.create(
            name="Laser Cutter", description="Laser", authorised=True
        )
        self.profile.interlocks.add(self.interlock)

        self.unassigned_interlock = Interlock.objects.create(
            name="CNC Router", description="CNC", authorised=True
        )

        self.reservation = InterlockReservation.objects.create(
            interlock=self.interlock,
            user=self.user,
            created_by=self.user,
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2),
        )

        InterlockReservation.objects.create(
            interlock=self.interlock,
            user=self.user,
            created_by=self.user,
            start_time=self.now - timedelta(days=1),
            end_time=self.now - timedelta(hours=20),
        )

    def test_only_accessible_interlocks_are_returned(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            "/api/access/interlock-reservations/",
            {"start": (self.now - timedelta(hours=1)).isoformat()},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["interlocks"]
        self.assertEqual(len(data), 1)

        interlock_data = data[0]
        self.assertEqual(interlock_data["id"], self.interlock.id)
        self.assertEqual(len(interlock_data["reservations"]), 1)
        self.assertEqual(
            interlock_data["reservations"][0]["id"], str(self.reservation.id)
        )

    def test_staff_can_view_all_reservations(self):
        staff_user = User.objects.create_user(
            email="admin@example.com", password="password"
        )
        staff_user.staff = True
        staff_user.save()
        Profile.objects.create(
            user=staff_user,
            screen_name="admin",
            first_name="Admin",
            last_name="User",
            phone="0412345670",
            state="active",
        )

        other_reservation = InterlockReservation.objects.create(
            interlock=self.unassigned_interlock,
            user=staff_user,
            created_by=staff_user,
            start_time=self.now + timedelta(hours=3),
            end_time=self.now + timedelta(hours=4),
        )

        self.client.force_authenticate(staff_user)
        response = self.client.get(
            "/api/access/interlock-reservations/",
            {
                "start": (self.now - timedelta(hours=1)).isoformat(),
                "end": (self.now + timedelta(days=2)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["interlocks"]
        ids = {entry["id"] for entry in data}
        self.assertIn(self.interlock.id, ids)
        self.assertIn(self.unassigned_interlock.id, ids)

        second = next(
            entry for entry in data if entry["id"] == self.unassigned_interlock.id
        )
        self.assertEqual(len(second["reservations"]), 1)
        self.assertEqual(second["reservations"][0]["id"], str(other_reservation.id))
