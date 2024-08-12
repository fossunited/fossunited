<template>
  <div class="flex">
    <div class="w-full">
      <div class="w-full" v-if="profile.data">
        <div class="prose p-4 pb-0">
          <h2 class="mb-1">My Profile</h2>
          <p class="text-sm mb-4">Edit your profile details</p>
        </div>
        <div class="flex flex-col my-2">
          <div class="relative">
            <img
              class="w-full aspect-[4.96/1]"
              :src="
                profile.data.cover_image ||
                '/assets/fossunited/images/defaults/user_profile_banner.png'
              "
              alt="Banner Image"
            />
            <div class="top-3 right-3 absolute flex gap-1">
              <FileUploader
                :fileTypes="'image/*'"
                :validateFile="validateFile"
                @success="(file) => setBannerImage(file)"
              >
                <template v-slot="{ openFileSelector }">
                  <Button
                    :variant="'outline'"
                    :size="'sm'"
                    icon="edit-3"
                    @click="openFileSelector"
                  />
                </template>
              </FileUploader>
              <Button
                v-if="profile.data.cover_image"
                icon="trash"
                variant="solid"
                theme="red"
                @click="setBannerImage({ file_url: '' })"
              />
            </div>
          </div>
          <div class="z-10 w-fit relative -mt-12 mx-6">
            <img
              class="aspect-square border-4 border-white rounded w-28"
              :src="
                profile.data.profile_photo ||
                '/assets/fossunited/images/defaults/user_profile_image.png'
              "
              alt="Profile Photo"
            />
            <FileUploader
              class="top-3 right-3 absolute"
              :fileTypes="'image/*'"
              :validateFile="validateFile"
              @success="(file) => setProfileImage(file)"
            >
              <template v-slot="{ openFileSelector }">
                <Button
                  :variant="'outline'"
                  :size="'sm'"
                  icon="edit-3"
                  @click="openFileSelector"
                />
              </template>
            </FileUploader>
          </div>
          <div class="flex flex-col md:grid md:grid-cols-2 gap-4 my-2 p-6">
            <Switch
              size="sm"
              label="Make Profile Private"
              description="Enabling this will make your profile unavailable to others. You will still be able to do the tasks that require profile creation."
              v-model="profile.data.is_private"
              @click="toggleProfilePrivacy()"
            />
            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">Basic Details</h4>
            </div>
            <FormControl
              label="Full Name &ast;"
              v-model="profile_dict.full_name"
              placeholder="Enter your full name"
            />
            <FormControl
              label="Email &ast;"
              v-model="profile_dict.user"
              placeholder="Enter your email"
              disabled
            />
            <div>
              <FormControl
                label="Username &ast;"
                v-model="profile_dict.username"
                placeholder="Enter your username"
              />
              <div class="mt-2 flex items-center">
                <div v-if="isValidUsername.loading">
                  <span class="text-sm text-gray-500 mr-2">
                    Checking availability...
                  </span>
                  <span
                    class="animate-spin h-4 w-4 border-2 border-gray-500 rounded-full border-t-transparent"
                  ></span>
                </div>
                <div
                  v-else-if="
                    profile_dict.username &&
                    !usernameValidateErrors &&
                    profile_dict.username !== initialUsername
                  "
                  class="flex"
                >
                  <span class="text-sm text-green-500 mr-2 font-semibold">
                    Username is available
                  </span>
                  <svg
                    class="h-4 w-4 text-green-700"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M5 13l4 4L19 7"
                    ></path>
                  </svg>
                </div>
              </div>
              <ErrorMessage :message="usernameValidateErrors" class="mt-2" />
            </div>
            <FormControl
              label="Short Tagline"
              v-model="profile_dict.bio"
              description="A short tagline about yourself"
            />
            <FormControl
              label="Current City"
              v-model="profile_dict.current_city"
            />
            <TextEditor
              label="About"
              class="col-span-2"
              placeholder="Tell more about yourself here."
              :modelValue="profile_dict.about"
              @update:modelValue="profile_dict.about = $event"
            />
            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">SOCIAL Links</h4>
            </div>
            <div class="col-span-2 text-sm text-gray-600">
              Enter the complete links to your social, including
              <code>https://</code>
            </div>
            <FormControl
              type="url"
              label="Website"
              v-model="profile_dict.website"
            />
            <FormControl
              type="url"
              label="Twitter / X"
              v-model="profile_dict.x"
            />
            <FormControl
              type="url"
              label="LinkedIn"
              v-model="profile_dict.linkedin"
            />
            <FormControl
              type="url"
              label="GitHub"
              v-model="profile_dict.github"
            />
            <FormControl
              type="url"
              label="GitLab"
              v-model="profile_dict.gitlab"
            />
            <FormControl
              type="url"
              label="Instagram"
              v-model="profile_dict.instagram"
            />
            <FormControl
              type="url"
              label="YouTube"
              v-model="profile_dict.youtube"
            />
            <FormControl
              type="url"
              label="Dev.to"
              v-model="profile_dict.devto"
            />
            <FormControl
              type="url"
              label="Medium"
              v-model="profile_dict.medium"
            />
            <FormControl
              type="url"
              label="Mastodon"
              v-model="profile_dict.mastodon"
            />
            <ErrorMessage class="col-span-2" :message="updateErrors" />
            <div class="hidden md:block"></div>
            <div class="flex justify-end">
              <Button
                :variant="'solid'"
                :size="'md'"
                :theme="'green'"
                label="Save"
                class="w-full md:w-2/3"
                @click="handleUpdateProfile()"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import TextEditor from '@/components/TextEditor.vue'
import {
  createResource,
  FileUploader,
  Switch,
  FormControl,
  ErrorMessage,
} from 'frappe-ui'

import { reactive, ref, watch, computed } from 'vue'
import { toast } from 'vue-sonner'

const profile_dict = reactive({
  full_name: '',
  user: '',
  username: '',
  bio: '',
  current_city: '',
  about: '',
  website: '',
  x: '',
  linkedin: '',
  github: '',
  gitlab: '',
  instagram: '',
  youtube: '',
  devto: '',
  medium: '',
  mastodon: '',
})

const profile = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
  auto: true,
  onSuccess(data) {
    Object.keys(profile_dict).forEach((key) => {
      profile_dict[key] = data[key]
    })
  },
})

const validateFile = (file) => {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg'].includes(extn)) {
    return 'Only PNG and JPG images are allowed'
  }
}

const setBannerImage = (_file) => {
  createResource({
    url: 'fossunited.api.profile.set_cover_image',
    makeParams() {
      return {
        file_url: _file.file_url,
      }
    },
    auto: true,
    onSuccess() {
      if (_file.file_url) {
        toast.success('Banner Image Updated')
      } else {
        toast.success('Banner Image Removed')
      }
      profile.fetch()
    },
  })
}

const setProfileImage = (_file) => {
  createResource({
    url: 'fossunited.api.profile.set_profile_image',
    makeParams() {
      return {
        file_url: _file.file_url,
      }
    },
    auto: true,
    onSuccess() {
      profile.fetch()
      toast.success('Profile Image Updated')
    },
    onError(err) {
      toast.error('Error updating profile image' + err)
    },
  })
}

const toggleProfilePrivacy = () => {
  createResource({
    url: 'fossunited.api.profile.toggle_profile_privacy',
    makeParams() {
      return {
        value: profile.data.is_private,
      }
    },
    auto: true,
    onSuccess() {
      if (profile.data.is_private) {
        toast.info('Profile is now private')
      } else {
        toast.info('Profile is now public')
      }
      profile.fetch()
    },
  })
}

const updateErrors = ref('')

const updateProfileErrors = () => {
  const errors = []
  if (!profile_dict.full_name) errors.push('Full Name is required')
  if (!profile_dict.username) errors.push('Username is required')
  if (!profile_dict.user) errors.push('Email is required')
  return errors
}

const initialUsername = computed(() => profile.data?.username || '')
const usernameValidateErrors = ref('')

const usernameErrors = () => {
  const _errors = []
  const messages = [
    'Username must be at least 3 characters long.',
    'Username can only contain letters, numbers, underscores and dots.',
    'Username cannot end with extensions like .txt, .html, etc.',
  ]
  if (!profile_dict.username) {
    _errors.push('Username is required')
    return _errors
  }
  if (profile_dict.username.length < 3) {
    _errors.push(messages[0])
  }
  if (!/^[a-zA-Z0-9_\.]+$/.test(profile_dict.username)) {
    _errors.push(messages[1])
  }
  if (/\.(txt|html|php|js|css|htm)$/i.test(profile_dict.username)) {
    _errors.push(messages[2])
  }
  return _errors
}

const validateUsername = () => {
  const errors = usernameErrors()

  if (errors.length) {
    usernameValidateErrors.value = errors.join(', ')
  } else if (profile_dict.username !== initialUsername.value) {
    usernameValidateErrors.value = ''
    isValidUsername
      .fetch()
      .then(() => {
        if (!isValidUsername.data) {
          usernameValidateErrors.value = 'Username is not available'
        } else {
          usernameValidateErrors.value = ''
        }
      })
      .catch(() => {
        usernameValidateErrors.value =
          'Error checking username availability. Refresh and try again!'
      })
  } else {
    usernameValidateErrors.value = ''
  }
}

watch(
  () => profile_dict.username,
  (newValue, oldValue) => {
    if (newValue !== oldValue) {
      usernameValidateErrors.value = ''
      if (newValue.trim() !== '') {
        validateUsername()
      }
    }
  },
  { immediate: false },
)

const isValidUsername = createResource({
  url: 'fossunited.api.profile.is_valid_username',
  makeParams() {
    return {
      username: profile_dict.username,
      id: profile.data.name,
    }
  },
})

const updateProfile = createResource({
  url: 'fossunited.api.profile.update_profile',
  makeParams() {
    return {
      fields_dict: profile_dict,
    }
  },
  onSuccess() {
    toast.success('Profile Updated Successfully')
    profile.fetch()
  },
  onError(err) {
    toast.error('Error updating profile: ' + err.messages)
  },
})

const handleUpdateProfile = () => {
  const errors = updateProfileErrors()
  if (errors.length) {
    updateErrors.value = errors.join(', ')
    return
  }
  updateErrors.value = ''
  if (usernameValidateErrors.value) {
    return
  }
  updateProfile.fetch()
}
</script>
