<template>
  <q-page class="row flex content-start justify-center q-pa-md">
    <div class="column info-container">
      <q-card class="q-mb-md">
        <q-card-section>
          <div class="text-h5 q-mb-sm">
            {{ $t('information.about.title', { siteName }) }}
          </div>
          <div class="text-body1">
            {{ $t('information.about.description', { siteName, siteOwner }) }}
          </div>
        </q-card-section>

        <q-separator />

        <q-card-section>
          <div class="text-subtitle1 q-mb-sm">
            {{ $t('information.about.highlightsTitle') }}
          </div>
          <q-list dense>
            <q-item v-for="(highlight, index) in highlights" :key="index">
              <q-item-section avatar>
                <q-icon :name="icons.info" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ highlight }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>

      <q-card>
        <q-card-section>
          <div class="text-subtitle1 q-mb-sm">
            {{ $t('information.about.contactTitle') }}
          </div>
          <div class="text-body1 q-mb-md">
            {{ $t('information.about.contactDescription') }}
          </div>

          <q-list bordered separator>
            <q-item
              v-for="detail in contactDetails"
              :key="detail.label"
              :clickable="Boolean(detail.link)"
              :tag="detail.link ? 'a' : 'div'"
              :href="detail.link"
              :target="detail.link ? '_blank' : undefined"
              :rel="detail.link ? 'noopener' : undefined"
            >
              <q-item-section avatar>
                <q-icon :name="detail.icon" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ detail.label }}</q-item-label>
                <q-item-label caption>{{ detail.value }}</q-item-label>
              </q-item-section>
            </q-item>
            <q-item v-if="!contactDetails.length">
              <q-item-section>
                <q-item-label>{{
                  $t('information.about.noContact')
                }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script>
import { mapGetters } from 'vuex';
import icons from 'src/icons';

export default {
  name: 'InformationAboutPage',
  computed: {
    ...mapGetters('config', ['siteName', 'siteOwner', 'contact']),
    icons() {
      return icons;
    },
    highlights() {
      return [
        this.$t('information.about.highlights.membership'),
        this.$t('information.about.highlights.community'),
        this.$t('information.about.highlights.tools'),
        this.$t('information.about.highlights.support'),
      ];
    },
    contactDetails() {
      const details = [];
      const contact = this.contact || {};

      const addDetail = (value, label, icon, linkFormatter) => {
        const trimmed = (value || '').trim();
        if (!trimmed) {
          return;
        }

        details.push({
          label,
          value: trimmed,
          icon,
          link: linkFormatter ? linkFormatter(trimmed) : null,
        });
      };

      addDetail(
        contact.admin,
        this.$t('information.labels.generalContact'),
        icons.email,
        (value) => `mailto:${value}`
      );
      addDetail(
        contact.sysadmin,
        this.$t('information.labels.sysadminContact'),
        icons.email,
        (value) => `mailto:${value}`
      );
      addDetail(
        contact.address,
        this.$t('information.labels.postalAddress'),
        icons.location
      );
      addDetail(
        contact.phone,
        this.$t('information.labels.phone'),
        icons.phone,
        (value) => `tel:${value}`
      );
      addDetail(
        contact.twitter,
        this.$t('information.labels.twitter'),
        icons.twitter,
        (value) =>
          value.startsWith('http')
            ? value
            : `https://twitter.com/${value.replace(/^@/, '')}`
      );
      addDetail(
        contact.facebook,
        this.$t('information.labels.facebook'),
        icons.facebook,
        (value) =>
          value.startsWith('http')
            ? value
            : `https://facebook.com/${value.replace(/^@/, '')}`
      );

      return details;
    },
  },
};
</script>

<style lang="sass" scoped>
.info-container
  width: 100%
  max-width: $maxWidth
</style>
