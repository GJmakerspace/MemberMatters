<template>
  <q-page class="q-pa-md interlock-reservations-page relative-position">
    <div class="text-h5 q-mb-xs">{{ $t('interlockReservations.title') }}</div>
    <div class="text-body2 q-mb-md">
      {{ $t('interlockReservations.description') }}
    </div>

    <q-banner v-if="loadError" class="bg-negative text-white q-mb-md">
      {{ loadError }}
    </q-banner>

    <q-card flat bordered class="q-mb-md">
      <q-card-section>
        <div class="row items-start q-col-gutter-md">
          <div class="col-auto">
            <q-date
              v-model="selectedDate"
              minimal
              color="primary"
              mask="YYYY-MM-DD"
              @update:model-value="handleDateChange"
            />
          </div>
          <div class="col">
            <div class="row items-center q-mb-sm">
              <div class="text-subtitle1">{{ formattedSelectedDate }}</div>
              <q-space />
              <q-btn
                dense
                flat
                round
                :icon="icons.sync"
                :disable="loading"
                @click="loadInterlockReservations"
              />
            </div>
            <div class="text-caption text-grey-7">
              {{ $t('interlockReservations.calendarHint') }}
            </div>
            <div class="calendar-hours row no-wrap q-mt-sm">
              <div
                v-for="hour in hours"
                :key="hour"
                class="calendar-hour text-caption"
              >
                {{ formatHour(hour) }}
              </div>
            </div>
          </div>
        </div>
      </q-card-section>
    </q-card>

    <q-inner-loading :showing="loading">
      <q-spinner color="primary" size="42px" />
    </q-inner-loading>

    <div v-if="!loading && interlocks.length === 0" class="text-body2">
      {{ $t('interlockReservations.noInterlocks') }}
    </div>

    <div v-else class="column">
      <q-card
        v-for="interlock in interlocks"
        :key="interlock.id"
        bordered
        class="q-mb-lg"
      >
        <q-card-section class="q-pb-none">
          <div class="row items-center q-col-gutter-sm">
            <div class="text-subtitle1">{{ interlock.name }}</div>
            <q-badge v-if="interlock.lockedOut" color="orange" class="q-ml-xs">
              {{ $t('access.maintenance') }}
            </q-badge>
            <q-badge v-if="interlock.offline" color="grey" class="q-ml-xs">
              {{ $t('device.offlineStatus') }}
            </q-badge>
            <q-space />
            <q-btn
              size="sm"
              color="primary"
              :icon="icons.add"
              :label="$t('interlockReservations.newReservation')"
              @click="openReservationDialog(interlock)"
              :disable="interlock.lockedOut || loading"
            />
          </div>
          <div class="text-caption text-grey-7 q-mt-xs">
            {{ interlock.description }}
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <div class="reservation-track">
            <div
              class="reservation-grid-line"
              v-for="hour in hours"
              :key="hour"
              :style="gridLineStyle(hour)"
            />
            <div
              v-if="showCurrentTimeMarker"
              class="reservation-current-time"
              :style="currentTimeStyle"
            />
            <div
              v-for="reservation in dayReservations(interlock)"
              :key="reservation.id"
              class="reservation-block"
              :style="reservationStyle(reservation)"
            >
              <div class="row items-center justify-between">
                <div class="ellipsis">
                  <div class="text-weight-medium">
                    {{
                      reservation.userName ||
                      $t('interlockReservations.unassignedReservation')
                    }}
                  </div>
                  <div class="text-caption">
                    {{ formatReservationRange(reservation) }}
                  </div>
                </div>
                <q-btn
                  v-if="canCancel(reservation)"
                  dense
                  flat
                  round
                  size="sm"
                  color="negative"
                  :icon="icons.remove"
                  @click="confirmCancel(reservation)"
                />
              </div>
            </div>
          </div>
          <div
            v-if="dayReservations(interlock).length === 0"
            class="text-caption text-grey-7 q-mt-sm"
          >
            {{ $t('interlockReservations.noReservationsForDay') }}
          </div>
        </q-card-section>
      </q-card>
    </div>

    <q-dialog v-model="reservationDialog">
      <q-card style="min-width: 360px">
        <q-card-section class="row items-center q-gutter-sm q-pb-none">
          <q-icon :name="icons.calendar" />
          <div class="text-h6">
            {{ dialogTitle }}
          </div>
        </q-card-section>

        <q-card-section>
          <div class="row q-col-gutter-md">
            <div class="col-12">
              <q-input
                v-model="form.date"
                type="date"
                :label="$t('form.date')"
              />
            </div>
            <div class="col-6">
              <q-input
                v-model="form.startTime"
                type="time"
                :label="$t('interlockReservations.startTime')"
              />
            </div>
            <div class="col-6">
              <q-input
                v-model="form.endTime"
                type="time"
                :label="$t('interlockReservations.endTime')"
              />
            </div>
          </div>
          <div v-if="formError" class="text-negative text-caption q-mt-sm">
            {{ formError }}
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat :label="$t('button.cancel')" v-close-popup />
          <q-btn
            unelevated
            color="primary"
            :label="$t('interlockReservations.saveReservation')"
            :loading="savingReservation"
            @click="submitReservation"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import dayjs from 'dayjs';
import icons from '../icons';

export default {
  name: 'InterlockReservationsPage',
  data() {
    return {
      icons,
      loading: false,
      loadError: '',
      interlocks: [],
      selectedDate: dayjs().format('YYYY-MM-DD'),
      reservationDialog: false,
      activeInterlock: null,
      form: {
        date: dayjs().format('YYYY-MM-DD'),
        startTime: dayjs().add(1, 'hour').minute(0).second(0).format('HH:mm'),
        endTime: dayjs().add(2, 'hour').minute(0).second(0).format('HH:mm'),
      },
      savingReservation: false,
      formError: '',
    };
  },
  computed: {
    hours() {
      return Array.from({ length: 25 }, (_, i) => i);
    },
    formattedSelectedDate() {
      return dayjs(this.selectedDate).format('dddd, D MMMM YYYY');
    },
    dayStart() {
      return dayjs(this.selectedDate).startOf('day');
    },
    dayEnd() {
      return this.dayStart.add(1, 'day');
    },
    showCurrentTimeMarker() {
      return dayjs().isSame(this.selectedDate, 'day');
    },
    currentTimeStyle() {
      const minutesIntoDay = dayjs().diff(this.dayStart, 'minute');
      const percentage = Math.min(
        100,
        Math.max(0, (minutesIntoDay / (24 * 60)) * 100)
      );
      return { left: `${percentage}%` };
    },
    rangeStart() {
      return dayjs(this.selectedDate).startOf('month');
    },
    rangeEnd() {
      return this.rangeStart.add(1, 'month').endOf('day');
    },
    profile() {
      return this.$store.getters['profile/profile'];
    },
    dialogTitle() {
      const name = this.activeInterlock?.name || '';
      return this.$t('interlockReservations.createTitle', { name });
    },
  },
  methods: {
    handleDateChange() {
      this.loadInterlockReservations();
      this.form.date = this.selectedDate;
    },
    formatHour(hour) {
      return dayjs().hour(hour).minute(0).format('ha');
    },
    gridLineStyle(hour) {
      const percentage = (hour / 24) * 100;
      return { left: `${percentage}%` };
    },
    dayReservations(interlock) {
      return (interlock.reservations || []).filter(
        (reservation) =>
          dayjs(reservation.endTime).isAfter(this.dayStart) &&
          dayjs(reservation.startTime).isBefore(this.dayEnd) &&
          !reservation.cancelled
      );
    },
    reservationStyle(reservation) {
      const start = dayjs(reservation.startTime).isBefore(this.dayStart)
        ? this.dayStart
        : dayjs(reservation.startTime);
      const end = dayjs(reservation.endTime).isAfter(this.dayEnd)
        ? this.dayEnd
        : dayjs(reservation.endTime);
      const totalMinutes = this.dayEnd.diff(this.dayStart, 'minute');
      const startMinutes = start.diff(this.dayStart, 'minute');
      const duration = Math.max(end.diff(start, 'minute'), 1);
      return {
        left: `${(startMinutes / totalMinutes) * 100}%`,
        width: `${(duration / totalMinutes) * 100}%`,
      };
    },
    formatReservationRange(reservation) {
      const start = dayjs(reservation.startTime).format('h:mma');
      const end = dayjs(reservation.endTime).format('h:mma');
      return `${start} - ${end}`;
    },
    canCancel(reservation) {
      const profileId = this.profile?.id;
      const isStaff = this.profile?.permissions?.staff;
      return (
        isStaff ||
        reservation.userId === profileId ||
        reservation.createdById === profileId
      );
    },
    setDefaultTimes() {
      const startCandidate = dayjs(this.selectedDate).hour(dayjs().hour() + 1);
      const clampedStart = startCandidate.isAfter(this.dayEnd)
        ? this.dayEnd.subtract(1, 'hour')
        : startCandidate;
      const end = clampedStart.add(1, 'hour');

      this.form.date = this.selectedDate;
      this.form.startTime = clampedStart.format('HH:mm');
      this.form.endTime = end.format('HH:mm');
    },
    openReservationDialog(interlock) {
      this.activeInterlock = interlock;
      this.setDefaultTimes();
      this.formError = '';
      this.reservationDialog = true;
    },
    loadInterlockReservations() {
      this.loading = true;
      this.loadError = '';
      this.$axios
        .get('/api/access/interlock-reservations/', {
          params: {
            start: this.rangeStart.toISOString(),
            end: this.rangeEnd.toISOString(),
          },
        })
        .then((response) => {
          this.interlocks = response.data.interlocks || [];
        })
        .catch(() => {
          this.loadError = this.$t('error.requestFailed');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    submitReservation() {
      if (!this.activeInterlock) return;

      const startTime = dayjs(`${this.form.date} ${this.form.startTime}`);
      const endTime = dayjs(`${this.form.date} ${this.form.endTime}`);

      if (!startTime.isValid() || !endTime.isValid()) {
        this.formError = this.$t('interlockReservations.invalidDate');
        return;
      }

      if (!endTime.isAfter(startTime)) {
        this.formError = this.$t('interlockReservations.startAfterEnd');
        return;
      }

      this.savingReservation = true;
      this.formError = '';
      this.$axios
        .post(
          `/api/access/interlocks/${this.activeInterlock.id}/reservations/`,
          {
            startTime: startTime.toISOString(),
            endTime: endTime.toISOString(),
          }
        )
        .then((response) => {
          const reservation = response.data;
          this.interlocks = this.interlocks.map((item) => {
            if (item.id !== this.activeInterlock.id) return item;
            const reservations = [
              ...(item.reservations || []),
              reservation,
            ].sort((a, b) => dayjs(a.startTime).diff(dayjs(b.startTime)));
            return { ...item, reservations };
          });
          this.reservationDialog = false;
        })
        .catch((error) => {
          if (error.response?.data?.error === 'reservation_conflict') {
            this.formError = this.$t(
              'interlockReservations.reservationConflict'
            );
          } else {
            this.formError = this.$t('error.requestFailed');
          }
        })
        .finally(() => {
          this.savingReservation = false;
        });
    },
    confirmCancel(reservation) {
      this.$q
        .dialog({
          title: this.$t('interlockReservations.cancelTitle'),
          message: this.$t('interlockReservations.cancelMessage'),
          prompt: {
            model: '',
            type: 'text',
            label: this.$t('interlockReservations.cancelReason'),
          },
          cancel: true,
          persistent: true,
        })
        .onOk((reason) => this.cancelReservation(reservation, reason));
    },
    cancelReservation(reservation, reason) {
      this.$axios
        .post(`/api/access/interlock-reservations/${reservation.id}/cancel/`, {
          reason,
        })
        .then((response) => {
          const updated = response.data;
          this.interlocks = this.interlocks.map((interlock) => {
            if (interlock.id !== updated.interlockId) return interlock;
            const reservations = (interlock.reservations || []).map((entry) =>
              entry.id === updated.id ? updated : entry
            );
            return { ...interlock, reservations };
          });
        })
        .catch(() => {
          this.$q.dialog({
            title: this.$t('error.error'),
            message: this.$t('error.requestFailed'),
          });
        });
    },
  },
  mounted() {
    this.loadInterlockReservations();
  },
};
</script>

<style lang="sass" scoped>
.interlock-reservations-page
  max-width: 1200px
  margin: 0 auto

.calendar-hours
  width: 100%

.calendar-hour
  flex: 1 0 auto
  text-align: center
  color: $grey-7

.reservation-track
  position: relative
  min-height: 70px
  border: 1px solid $grey-4
  border-radius: $generic-border-radius
  padding: 8px
  background: rgba(0, 0, 0, 0.02)
  overflow: hidden

.reservation-grid-line
  position: absolute
  top: 0
  bottom: 0
  width: 1px
  background: $grey-4

.reservation-current-time
  position: absolute
  top: 0
  bottom: 0
  width: 2px
  background: rgba($primary, 0.8)

.reservation-block
  position: absolute
  top: 12px
  min-width: 8%
  background: rgba($primary, 0.16)
  border: 1px solid rgba($primary, 0.45)
  border-radius: $generic-border-radius
  padding: 6px
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08)
  overflow: hidden

  .ellipsis
    min-width: 0

  .text-weight-medium
    font-size: 14px

  .text-caption
    white-space: nowrap
</style>
