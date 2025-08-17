<template>
  <div class="flex">
    <div class="w-full">
      <div v-if="profile.data" class="w-full">
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
                :file-types="'image/*'"
                :validate-file="validateFile"
                @success="(file) => setBannerImage(file)"
              >
                <template #default="{ openFileSelector }">
                  <Button
                    :variant="'outline'"
                    :size="'sm'"
                    icon="edit-3"
                    aria-label="Edit Banner Image"
                    title="Edit Banner Image"
                    @click="openFileSelector"
                  >
                  </Button>
                </template>
              </FileUploader>
              <Button
                v-if="profile.data.cover_image"
                icon="trash"
                variant="solid"
                theme="red"
                aria-label="Remove Banner Image"
                title="Remove Banner Image"
                @click="setBannerImage({ file_url: '' })"
              >
              </Button>
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
              :file-types="'image/*'"
              :validate-file="validateFile"
              @success="(file) => setProfileImage(file)"
            >
              <template #default="{ openFileSelector }">
                <Button
                  :variant="'outline'"
                  :size="'sm'"
                  icon="edit-3"
                  aria-label="Edit Profile Picture"
                  title="Edit Profile Picture"
                  @click="openFileSelector"
                >
                </Button>
              </template>
            </FileUploader>
          </div>
          <div class="flex flex-col md:grid md:grid-cols-2 gap-4 my-2 p-6">
            <Switch
              v-model="profile.data.is_private"
              size="sm"
              label="Make Profile Private"
              description="Enabling this will make your profile unavailable to others. You will still be able to do the tasks that require profile creation."
              aria-label="Make Profile Private"
              title="Make Profile Private"
              @click="toggleProfilePrivacy()"
            />
            <Switch
              v-model="profile.data.show_activity"
              size="sm"
              label="Show Community Activity"
              description="Enabling this will allow others to view which FOSS United events you have attended till date."
              aria-label="Show Community Activity"
              title="Show Community Activity"
              @click="toggleShowActivity()"
            />
            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">Basic Details</h4>
            </div>
            <FormControl
              v-model="profile_dict.full_name"
              label="Full Name &ast;"
              placeholder="Enter your full name"
            />
            <FormControl
              v-model="profile_dict.user"
              label="Email &ast;"
              placeholder="Enter your email"
              disabled
            />
            <div>
              <FormControl
                v-model="profile_dict.username"
                label="Username &ast;"
                placeholder="Enter your username"
              />
              <div class="mt-2 flex items-center">
                <div v-if="isValidUsername.loading">
                  <span class="text-sm text-gray-500 mr-2"> Checking availability... </span>
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
                  <span class="text-sm text-green-500 mr-1 font-semibold">
                    Username is available
                  </span>
                  <IconCheck class="h-4 w-4 text-green-500" />
                </div>
              </div>
              <ErrorMessage :message="usernameValidateErrors" class="mt-2" />
            </div>
            <FormControl
              v-model="profile_dict.cfp_visibility"
              type="select"
              :options="[
                {
                  label: 'Everyone',
                  value: 'Everyone',
                },
                {
                  label: 'Chapter Volunteers',
                  value: 'Chapter Volunteers',
                },
                {
                  label: 'Only Me',
                  value: 'Only Me',
                },
              ]"
              label="CFP Visibility"
              description="Chose who all can see the CFP Proposals you have made till date"
            />
            <FormControl
              v-model="profile_dict.bio"
              label="Short Tagline"
              description="A short tagline about yourself"
            />
            <FormControl v-model="profile_dict.current_city" label="Current City" />
            <TextEditor
              label="About"
              class="col-span-2"
              placeholder="Tell more about yourself here."
              :model-value="profile_dict.about"
              @update:model-value="profile_dict.about = $event"
            />
            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">SOCIAL Links</h4>
            </div>
            <div class="col-span-2 text-sm text-gray-600">
              Enter the complete links to your social, including
              <code>http(s)://</code>
            </div>
            <FormControl v-model="profile_dict.website" type="url" label="Website" />
            <FormControl v-model="profile_dict.x" type="url" label="Twitter / X" />
            <FormControl v-model="profile_dict.linkedin" type="url" label="LinkedIn" />
            <FormControl v-model="profile_dict.github" type="url" label="GitHub" />
            <FormControl v-model="profile_dict.gitlab" type="url" label="GitLab" />
            <FormControl v-model="profile_dict.instagram" type="url" label="Instagram" />
            <FormControl v-model="profile_dict.youtube" type="url" label="YouTube" />
            <FormControl v-model="profile_dict.devto" type="url" label="Dev.to" />
            <FormControl v-model="profile_dict.medium" type="url" label="Medium" />
            <FormControl v-model="profile_dict.mastodon" type="url" label="Mastodon" />

            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">Education Details</h4>
            </div>

            <div
              v-for="(edu, index) in profile_dict.education"
              :key="index"
              class="grid [grid-template-columns:auto_auto_auto_auto_auto_40px] gap-4 my-2 col-span-2"
            >
              <FormControl
                v-model="profile_dict.education[index].institution"
                label="College/Institute"
              />
              <FormControl v-model="profile_dict.education[index].degree" label="Degree" />
              <FormControl
                v-model="profile_dict.education[index].field_of_study"
                label="Field of Study"
              />
              <FormControl v-model="profile_dict.education[index].start_year" label="Start Year" />
              <FormControl v-model="profile_dict.education[index].end_year" label="End Year" />
              <button
                class="h-7 bg-gray-200 hover:bg-red-600 text-white text-xs rounded self-end"
                @click="deleteItem('education', index)"
              >
                ✕
              </button>
            </div>

            <div class="col-span-2 mt-2">
              <Button variant="solid" size="md" theme="gray" @click="addEducation">
                + Add More
              </Button>
            </div>

            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">Work Experience</h4>
            </div>

            <div
              v-for="(work, index) in profile_dict.experience"
              :key="index"
              class="grid [grid-template-columns:auto_auto_auto_auto_auto_40px] gap-4 my-2 col-span-2"
            >
              <FormControl v-model="profile_dict.experience[index].title" label="Job Title" />
              <FormControl v-model="profile_dict.experience[index].company" label="Company" />
              <FormControl
                v-model="profile_dict.experience[index].company_website"
                label="Company Website"
                type="url"
              />
              <FormControl
                v-model="profile_dict.experience[index].employment_type"
                label="Employment Type"
                type="select"
                :options="[
                  { label: 'Full-time', value: 'Full-time' },
                  { label: 'Part-time', value: 'Part-time' },
                  { label: 'Internship', value: 'Internship' },
                  { label: 'Freelance', value: 'Freelance' },
                  { label: 'Self-employed', value: 'Self-employed' },
                  { label: 'Trainee', value: 'Trainee' },
                ]"
              />
              <FormControl
                v-model="profile_dict.experience[index].start_date"
                label="Start Date"
                type="date"
              />
              <button
                class="h-7 bg-gray-200 hover:bg-red-600 text-white text-xs rounded self-end"
                @click="deleteItem('experience', index)"
              >
                ✕
              </button>
            </div>

            <div class="col-span-2 mt-2">
              <Button variant="solid" size="md" theme="gray" @click="addWorkExp">
                + Add More
              </Button>
            </div>

            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">Project Details</h4>
            </div>

            <div
              v-for="(proj, index) in profile_dict.projects"
              :key="index"
              class="grid [grid-template-columns:auto_auto_auto_auto_40px] gap-4 my-2 col-span-2"
            >
              <FormControl
                v-model="profile_dict.projects[index].project_name"
                label="Project Name"
              />
              <FormControl
                v-model="profile_dict.projects[index].project_link"
                label="Project Link"
                type="url"
              />
              <FormControl v-model="profile_dict.projects[index].tagline" label="Tagline" />
              <FormControl
                v-model="profile_dict.projects[index].cover_image"
                label="Cover Image"
                type="url"
              />
              <button
                class="h-7 bg-gray-200 hover:bg-red-600 text-white text-xs rounded self-end"
                @click="deleteItem('projects', index)"
              >
                ✕
              </button>
            </div>

            <div class="col-span-2 mt-2">
              <Button variant="solid" size="md" theme="gray" @click="addProjects">
                + Add More
              </Button>
            </div>

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
import TextEditor from '@/components/ui/TextEditor.vue'
import { IconCheck } from '@tabler/icons-vue'
import { createResource, FileUploader, Switch, FormControl, ErrorMessage } from 'frappe-ui'

import { reactive, ref, watch, computed } from 'vue'
import { toast } from 'vue-sonner'

const profile_dict = reactive({
  full_name: '',
  user: '',
  username: '',
})

function deepAssign(target, source) {
  for (const key in source) {
    if (Array.isArray(source[key])) {
      // Replace entire array (or you can go deeper if needed)
      target[key] = source[key]
    } else if (source[key] !== null && typeof source[key] === 'object') {
      if (!target[key] || typeof target[key] !== 'object') {
        target[key] = {}
      }
      deepAssign(target[key], source[key])
    } else {
      target[key] = source[key]
    }
  }
}

const profile = createResource({
  url: 'fossunited.api.dashboard.get_session_user_profile',
  auto: true,
  onSuccess(data) {
    // assignValues(profile_dict, data)
    deepAssign(profile_dict, data)
    const eduLength = Array.isArray(profile_dict.education) ? profile_dict.education.length : 0
    // console.log('Updated PROFILE_DICT:', JSON.stringify(profile_dict, null, 2))
    // console.log('Updated DATA:', JSON.stringify(data, null, 2))
    // console.log('Updated EDUCATION:', JSON.stringify(profile_dict.education.length, null, 2))
  },
})

const validateFile = (file) => {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg', 'jpeg'].includes(extn)) {
    updateErrors.value = 'Only PNG and JPG images are allowed'
    toast.error(updateErrors.value)
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

const toggleShowActivity = () => {
  createResource({
    url: 'fossunited.api.profile.toggle_show_activity',
    makeParams() {
      return {
        value: profile.data.show_activity,
      }
    },
    auto: true,
    onSuccess() {
      if (profile.data.show_activity) {
        toast.info('Community Activity will be shown on your profile page now')
      } else {
        toast.info("Community Activity won't be shown on your profile page now")
      }
      profile.fetch()
    },
  })
}

const updateErrors = ref('')

const isValidUrl = (url) => {
  try {
    const parsed = new URL(url)
    return parsed.protocol === 'http:' || parsed.protocol === 'https:'
  } catch (_) {
    return false
  }
}

const updateProfileErrors = () => {
  const errors = []
  if (!profile_dict.full_name.trim()) errors.push('\nFull Name is required')
  if (!profile_dict.username.trim()) errors.push('\nUsername is required')
  if (!profile_dict.user.trim()) errors.push('\nEmail is required')

  const socials = {
    website: profile_dict.website,
    x: profile_dict.x,
    linkedin: profile_dict.linkedin,
    github: profile_dict.github,
    gitlab: profile_dict.gitlab,
    instagram: profile_dict.instagram,
    youtube: profile_dict.youtube,
    devto: profile_dict.devto,
    medium: profile_dict.medium,
    mastodon: profile_dict.mastodon,
  }
  Object.keys(socials).forEach((key) => {
    const url = socials[key]
    if (url && !isValidUrl(url)) {
      errors.push(`\n${key} is not a valid url`)
    }
  })
  return errors
}

const initialUsername = computed(() => profile.data?.username ?? '')
const usernameValidateErrors = ref('')

const getUsernameErrors = () => {
  const _errors = []
  const messages = [
    'Username must be between 3 and 30 characters',
    'Username can only contain letters, numbers, underscores and dots.',
    'Username cannot end with extensions like .txt, .html, etc.',
  ]
  if (!profile_dict.username) {
    _errors.push('Username is required')
    return _errors
  }
  if (profile_dict.username.length < 3 || profile_dict.username.length > 30) {
    _errors.push(messages[0])
  }
  if (!/^[a-zA-Z0-9_\.]+$/.test(profile_dict.username)) {
    _errors.push(messages[1])
  }
  if (/\.(txt|html|php|js|json|xml|css|htm)$/i.test(profile_dict.username)) {
    _errors.push(messages[2])
  }
  return _errors
}

const validateUsername = async () => {
  const errors = getUsernameErrors()

  if (errors.length !== 0) {
    usernameValidateErrors.value = errors.join(', ')
  } else if (profile_dict.username !== initialUsername.value) {
    usernameValidateErrors.value = ''
    try {
      await isValidUsername.fetch()

      if (!isValidUsername.data) {
        usernameValidateErrors.value = 'Username is not available'
      } else {
        usernameValidateErrors.value = ''
      }
    } catch (_) {
      usernameValidateErrors.value = 'Error checking username availability. Refresh and try again!'
    }
  } else {
    usernameValidateErrors.value = ''
  }
}

watch(
  () => profile_dict.username,
  (newValue) => {
    usernameValidateErrors.value = ''
    if (newValue.trim() !== '') {
      validateUsername()
    }
  },
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

function addEducation() {
  profile_dict.education.push({
    institution: '',
    degree: '',
    field_of_study: '',
    start_year: '',
    end_year: '',
  })
}

function addWorkExp() {
  profile_dict.experience.push({
    title: '',
    company: '',
    company_website: '',
    employment_type: '',
    start_date: '',
  })
}

function addProjects() {
  profile_dict.projects.push({
    project_title: '',
    project_link: '',
    tagline: '',
  })
}

function deleteItem(field, index) {
  if (!['projects', 'education', 'experience'].includes(field)) {
    console.warn(`Invalid field: ${field}`)
    return
  }

  const list = profile_dict[field]
  if (Array.isArray(list) && index > -1 && index < list.length) {
    list.splice(index, 1)
  }
}

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
