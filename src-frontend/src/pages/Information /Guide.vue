<template>
  <q-page class="row flex content-start justify-center q-pa-md">
    <div class="column info-container">
      <q-card class="q-mb-md">
        <q-card-section>
          <div class="text-h5 q-mb-sm">
            {{ $t('information.guide.title', { siteName }) }}
          </div>
          <div class="text-body1">
            {{ $t('information.guide.introduction', { siteName }) }}
          </div>
        </q-card-section>
      </q-card>

      <q-card
        v-for="section in guideSections"
        :key="section.title"
        class="q-mb-md"
      >
        <q-card-section>
          <div class="text-subtitle1 q-mb-sm">{{ section.title }}</div>
          <div v-if="section.description" class="text-body1 q-mb-sm">
            {{ section.description }}
          </div>
          <q-list dense>
            <q-item v-for="item in section.items" :key="item.title">
              <q-item-section avatar>
                <q-icon :name="item.icon" color="primary" />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ item.title }}</q-item-label>
                <q-item-label caption>{{ item.caption }}</q-item-label>
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
  name: 'InformationGuidePage',
  computed: {
    ...mapGetters('config', ['siteName']),
    guideSections() {
      return [
        {
          title: this.$t('information.guide.gettingStarted.title'),
          description: this.$t('information.guide.gettingStarted.description'),
          items: [
            {
              title: this.$t('information.guide.gettingStarted.profile.title'),
              caption: this.$t(
                'information.guide.gettingStarted.profile.caption'
              ),
              icon: icons.profile,
            },
            {
              title: this.$t('information.guide.gettingStarted.access.title'),
              caption: this.$t(
                'information.guide.gettingStarted.access.caption'
              ),
              icon: icons.checkAccess,
            },
            {
              title: this.$t('information.guide.gettingStarted.billing.title'),
              caption: this.$t(
                'information.guide.gettingStarted.billing.caption'
              ),
              icon: icons.billing,
            },
          ],
        },
        {
          title: this.$t('information.guide.onsite.title'),
          description: this.$t('information.guide.onsite.description'),
          items: [
            {
              title: this.$t('information.guide.onsite.signin.title'),
              caption: this.$t('information.guide.onsite.signin.caption'),
              icon: icons.signin,
            },
            {
              title: this.$t('information.guide.onsite.swipes.title'),
              caption: this.$t('information.guide.onsite.swipes.caption'),
              icon: icons.recentSwipes,
            },
            {
              title: this.$t('information.guide.onsite.rules.title'),
              caption: this.$t('information.guide.onsite.rules.caption'),
              icon: icons.info,
            },
          ],
        },
        {
          title: this.$t('information.guide.support.title'),
          description: this.$t('information.guide.support.description'),
          items: [
            {
              title: this.$t('information.guide.support.issue.title'),
              caption: this.$t('information.guide.support.issue.caption'),
              icon: icons.reportIssue,
            },
            {
              title: this.$t('information.guide.support.contact.title'),
              caption: this.$t('information.guide.support.contact.caption'),
              icon: icons.email,
            },
            {
              title: this.$t('information.guide.support.updates.title'),
              caption: this.$t('information.guide.support.updates.caption'),
              icon: icons.stats,
            },
          ],
        },
      ];
    },
  },
};
</script>

<style lang="sass" scoped>
.info-container
  width: 100%
  max-width: $maxWidth
</style>
