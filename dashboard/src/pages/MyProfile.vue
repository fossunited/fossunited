<template>
  <div class="flex">
    <div class="w-full">
      <div v-if="profileDoc?.doc" class="w-full">
        <div class="prose p-4 pb-0">
          <h2 class="mb-1">My Profile</h2>
          <p class="text-sm mb-4">Edit your profile details</p>
        </div>
        <div class="flex flex-col my-2">
          <div class="relative">
            <img
              class="w-full aspect-[4.96/1]"
              :src="
                profileDoc.doc.cover_image ||
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
                v-if="profileDoc.doc.cover_image"
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
                profileDoc.doc.profile_photo ||
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
              v-model="profileDoc.doc.is_private"
              size="sm"
              label="Make Profile Private"
              description="Enabling this will make your profile unavailable to others. You will still be able to do the tasks that require profile creation."
              aria-label="Make Profile Private"
              title="Make Profile Private"
              @update:model-value="toggleProfilePrivacy"
            />
            <Switch
              v-model="profileDoc.doc.show_activity"
              size="sm"
              label="Show Community Activity"
              description="Enabling this will allow others to view which FOSS United events you have attended till date."
              aria-label="Show Community Activity"
              title="Show Community Activity"
              @update:model-value="toggleShowActivity"
            />
            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">Basic Details</h4>
            </div>
            <FormControl
              v-model="profileDoc.doc.full_name"
              label="Full Name &ast;"
              placeholder="Enter your full name"
            />
            <FormControl
              v-model="profileDoc.doc.user"
              label="Email &ast;"
              placeholder="Enter your email"
              disabled
            />
            <div>
              <FormControl
              v-model="profileDoc.doc.username"
                label="Username &ast;"
                placeholder="Enter your username"
              />
              <div class="mt-2 flex items-center">
                <div v-if="isValidUsername.loading">
                  <span class="text-sm text-ink-gray-4 mr-2"> Checking availability... </span>
                  <span
                    class="animate-spin h-4 w-4 border-2 border-outline-gray-4 rounded-full border-t-transparent"
                  ></span>
                </div>
                <div
                  v-else-if="
                    profileDoc.doc.username &&
                    !usernameValidateErrors &&
                    profileDoc.doc.username !== initialUsername
                  "
                  class="flex"
                >
                  <span class="text-sm text-ink-green-2 mr-1 font-semibold">
                    Username is available
                  </span>
                  <IconCheck class="h-4 w-4 text-ink-green-2" />
                </div>
              </div>
              <ErrorMessage :message="usernameValidateErrors" class="mt-2" />
            </div>
            <FormControl
              v-model="profileDoc.doc.cfp_visibility"
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
              v-model="profileDoc.doc.bio"
              label="Short Tagline"
              description="A short tagline about yourself"
            />
            <FormControl v-model="profileDoc.doc.current_city" label="Current City" />
            <TextEditor
              label="About"
              class="col-span-2"
              placeholder="Tell more about yourself here."
              :model-value="profileDoc.doc.about"
              @update:model-value="profileDoc.doc.about = $event"
            />
            <div class="col-span-2 py-1 border-b">
              <h4 class="text-md font-medium uppercase">SOCIAL Links</h4>
            </div>
            <div class="col-span-2 text-sm text-ink-gray-5">
              Enter the complete links to your social, including
              <code>http(s)://</code>
            </div>
            <FormControl v-model="profileDoc.doc.website" type="url" label="Website" @blur="profileDoc.doc.website = ensureHttpsPrefix(profileDoc.doc.website)" />
            <FormControl v-model="profileDoc.doc.x" type="url" label="Twitter / X" @blur="profileDoc.doc.x = ensureHttpsPrefix(profileDoc.doc.x)" />
            <FormControl v-model="profileDoc.doc.linkedin" type="url" label="LinkedIn" @blur="profileDoc.doc.linkedin = ensureHttpsPrefix(profileDoc.doc.linkedin)" />
            <FormControl v-model="profileDoc.doc.github" type="url" label="GitHub" @blur="profileDoc.doc.github = ensureHttpsPrefix(profileDoc.doc.github)" />
            <FormControl v-model="profileDoc.doc.gitlab" type="url" label="GitLab" @blur="profileDoc.doc.gitlab = ensureHttpsPrefix(profileDoc.doc.gitlab)" />
            <FormControl v-model="profileDoc.doc.instagram" type="url" label="Instagram" @blur="profileDoc.doc.instagram = ensureHttpsPrefix(profileDoc.doc.instagram)" />
            <FormControl v-model="profileDoc.doc.youtube" type="url" label="YouTube" @blur="profileDoc.doc.youtube = ensureHttpsPrefix(profileDoc.doc.youtube)" />
            <FormControl v-model="profileDoc.doc.devto" type="url" label="Dev.to" @blur="profileDoc.doc.devto = ensureHttpsPrefix(profileDoc.doc.devto)" />
            <FormControl v-model="profileDoc.doc.medium" type="url" label="Medium" @blur="profileDoc.doc.medium = ensureHttpsPrefix(profileDoc.doc.medium)" />
            <FormControl v-model="profileDoc.doc.mastodon" type="url" label="Mastodon" @blur="profileDoc.doc.mastodon = ensureHttpsPrefix(profileDoc.doc.mastodon)" />
            <FormControl v-model="profileDoc.doc.bluesky" type="url" label="Bluesky" @blur="profileDoc.doc.bluesky = ensureHttpsPrefix(profileDoc.doc.bluesky)" />
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

            <!-- Projects -->
            <div class="col-span-2 py-1 border-b mt-2 flex items-center justify-between">
              <h4 class="text-md font-medium uppercase">Projects</h4>
              <Button
                v-if="!showAddProject"
                variant="outline"
                size="sm"
                icon="plus"
                label="Add Project"
                @click="openAddProject()"
              />
            </div>
            <div class="col-span-2 text-sm text-ink-gray-5">
              Add your open-source or personal projects to showcase on your profile.
            </div>

            <!-- existing project cards -->
            <div
              v-for="project in (profileDoc?.doc?.projects ?? [])"
              :key="project.name"
              class="col-span-2 border rounded-lg p-4 flex flex-col gap-3"
            >
              <div v-if="editingProject?.name !== project.name" class="flex justify-between items-start gap-2">
                <div class="flex-1 min-w-0">
                  <p class="font-medium truncate">{{ project.project_name }}</p>
                  <p class="text-sm text-ink-gray-5 truncate">{{ project.tagline }}</p>
                  <a
                    :href="project.project_link"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-sm text-ink-blue-3 hover:underline break-all"
                  >{{ project.project_link }}</a>
                </div>
                <div class="flex gap-1 shrink-0">
                  <Button
                    icon="edit-3"
                    variant="ghost"
                    size="sm"
                    :title="`Edit ${project.project_name}`"
                    @click="startEditProject(project)"
                  />
                  <Button
                    icon="trash"
                    variant="ghost"
                    size="sm"
                    theme="red"
                    :title="`Delete ${project.project_name}`"
                    @click="deleteProject(project.name)"
                  />
                </div>
              </div>

              <!-- inline edit form -->
              <div v-else class="flex flex-col gap-3">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <FormControl
                    v-model="editingProject.project_name"
                    label="Project Name *"
                    placeholder="My Awesome Project"
                  />
                  <FormControl
                    v-model="editingProject.project_link"
                    label="Project Link *"
                    type="url"
                    placeholder="https://github.com/..."
                    @blur="editingProject.project_link = ensureHttpsPrefix(editingProject.project_link)"
                  />
                  <FormControl
                    v-model="editingProject.tagline"
                    label="Tagline *"
                    placeholder="A short description"
                    class="md:col-span-2"
                  />
                  <FormControl
                    v-model="editingProject.cover_image"
                    label="Cover Image URL (optional)"
                    placeholder="https://..."
                    class="md:col-span-2"
                  />
                </div>
                <ErrorMessage :message="projectErrors" />
                <div class="flex gap-2 justify-end">
                  <Button variant="outline" size="sm" label="Cancel" @click="cancelEditProject()" />
                  <Button
                    variant="solid"
                    size="sm"
                    theme="green"
                    label="Save"
                    :loading="profileDoc?.save?.loading"
                    @click="saveEditProject()"
                  />
                </div>
              </div>
            </div>

            <!-- add new project form -->
            <div v-if="showAddProject" class="col-span-2 border rounded-lg p-4 flex flex-col gap-3">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <FormControl
                  v-model="newProject.project_name"
                  label="Project Name *"
                  placeholder="My Awesome Project"
                />
                <FormControl
                  v-model="newProject.project_link"
                  label="Project Link *"
                  type="url"
                  placeholder="https://github.com/..."
                  @blur="newProject.project_link = ensureHttpsPrefix(newProject.project_link)"
                />
                <FormControl
                  v-model="newProject.tagline"
                  label="Tagline *"
                  placeholder="A short description"
                  class="md:col-span-2"
                />
                <FormControl
                  v-model="newProject.cover_image"
                  label="Cover Image URL (optional)"
                  placeholder="https://..."
                  class="md:col-span-2"
                />
              </div>
              <ErrorMessage :message="projectErrors" />
              <div class="flex gap-2 justify-end">
                <Button variant="outline" size="sm" label="Cancel" @click="showAddProject = false" />
                <Button
                  variant="solid"
                  size="sm"
                  theme="green"
                  label="Add Project"
                  :loading="profileDoc?.save?.loading"
                  @click="handleAddProject()"
                />
              </div>
            </div>

            <!-- bottom of form: no lonely Add Project button needed here -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import TextEditor from '@/components/ui/TextEditor.vue'
import { IconCheck } from '@tabler/icons-vue'
import { createResource, createDocumentResource, FileUploader, Switch, FormControl, ErrorMessage } from 'frappe-ui'
import { isValidUrl, ensureHttpsPrefix } from '@/helpers/utils'
import { fetchSessionProfile, sessionProfileResource } from '@/data/session'

import { reactive, ref, watch, computed } from 'vue'
import { toast } from 'vue-sonner'
const profileDoc = ref(null)

fetchSessionProfile()

watch(
  () => sessionProfileResource.data,
  (data) => {
    if (data && !profileDoc.value) {
      profileDoc.value = createDocumentResource({
        doctype: 'FOSS User Profile',
        name: data.name,
        fields: ['*'],
        auto: true,
      })
    }
  },
  { immediate: true }
)

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
      profileDoc.value.get.submit()
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
      profileDoc.value.get.submit()
      toast.success('Profile Image Updated')
    },
    onError(err) {
      toast.error('Error updating profile image' + err)
    },
  })
}

const toggleProfilePrivacy = async (value) => {
  const previous = !value
  try {
    await profileDoc.value.setValue.submit({ is_private: value })
    toast.info(value ? 'Profile is now private' : 'Profile is now public')
  } catch (err) {
    profileDoc.value.doc.is_private = previous
    toast.error('Failed to update privacy setting')
    console.error(err)
  }
}

const toggleShowActivity = async (value) => {
  const previous = !value
  try {
    await profileDoc.value.setValue.submit({ show_activity: value })
    toast.info(
      value
        ? 'Community Activity will be shown on your profile page now'
        : "Community Activity won't be shown on your profile page now",
    )
  } catch (err) {
    profileDoc.value.doc.show_activity = previous
    toast.error('Failed to update activity setting')
    console.error(err)
  }
}

const updateErrors = ref('')

const updateProfileErrors = () => {
  const errors = []
  const doc = profileDoc.value?.doc
  if (!doc) return errors
  if (!doc.full_name?.trim()) errors.push('\nFull Name is required')
  if (!doc.username?.trim()) errors.push('\nUsername is required')
  if (!doc.user?.trim()) errors.push('\nEmail is required')

  const socials = ['website', 'x', 'linkedin', 'github', 'gitlab', 'instagram', 'youtube', 'devto', 'medium', 'mastodon', 'bluesky']
  socials.forEach((key) => {
    const url = doc[key]
    if (url && !isValidUrl(url)) {
      errors.push(`\n${key} is not a valid url`)
    }
  })
  return errors
}

const initialUsername = computed(() => profileDoc.value?.doc?.username ?? '')
const usernameValidateErrors = ref('')

const getUsernameErrors = () => {
  const _errors = []
  const messages = [
    'Username must be between 3 and 30 characters',
    'Username can only contain letters, numbers, underscores and dots.',
    'Username cannot end with extensions like .txt, .html, etc.',
  ]
  const username = profileDoc.value?.doc?.username
  if (!username) {
    _errors.push('Username is required')
    return _errors
  }
  if (username.length < 3 || username.length > 30) {
    _errors.push(messages[0])
  }
  if (!/^[a-zA-Z0-9_\.]+$/.test(username)) {
    _errors.push(messages[1])
  }
  if (/\.(txt|html|php|js|json|xml|css|htm)$/i.test(username)) {
    _errors.push(messages[2])
  }
  return _errors
}

const validateUsername = async () => {
  const errors = getUsernameErrors()

  if (errors.length !== 0) {
    usernameValidateErrors.value = errors.join(', ')
  } else if (profileDoc.value?.doc?.username !== initialUsername.value) {
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
  () => profileDoc.value?.doc?.username,
  (newValue) => {
    usernameValidateErrors.value = ''
    if (newValue?.trim()) {
      validateUsername()
    }
  },
)

const isValidUsername = createResource({
  url: 'fossunited.api.profile.is_valid_username',
  makeParams() {
    return {
      username: profileDoc.value?.doc?.username,
      id: profileDoc.value?.doc?.name,
    }
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
  profileDoc.value.save
    .submit()
    .then(() => toast.success('Profile Updated Successfully'))
    .catch((err) => toast.error('Error updating profile: ' + (err?.message || '')))
}


const showAddProject = ref(false)
const projectErrors = ref('')

const emptyProject = () => ({ project_name: '', project_link: '', tagline: '', cover_image: '' })
const newProject = reactive(emptyProject())
const editingProject = ref(null)

const validateProject = (p) => {
  if (!p.project_name?.trim()) return 'Project Name is required'
  if (!p.project_link?.trim()) return 'Project Link is required'
  if (!isValidUrl(p.project_link)) return 'Project Link must be a valid HTTP(S) URL'
  if (!p.tagline?.trim()) return 'Tagline is required'
  return ''
}

const openAddProject = () => {
  Object.assign(newProject, emptyProject())
  editingProject.value = null
  projectErrors.value = ''
  showAddProject.value = true
}

const handleAddProject = () => {
  if (!profileDoc.value?.doc) return
  const err = validateProject(newProject)
  if (err) { projectErrors.value = err; return }
  projectErrors.value = ''
  profileDoc.value.doc.projects.push({ ...newProject })
  profileDoc.value.save
    .submit()
    .then(() => {
      showAddProject.value = false
      Object.assign(newProject, emptyProject())
      toast.success('Project added')
    })
    .catch((e) => {
      profileDoc.value.get.submit()
      projectErrors.value = e?.message || 'Failed to add project'
    })
}

const startEditProject = (project) => {
  showAddProject.value = false
  editingProject.value = { ...project }
  projectErrors.value = ''
}

const cancelEditProject = () => {
  editingProject.value = null
  projectErrors.value = ''
}

const saveEditProject = () => {
  if (!profileDoc.value?.doc) return
  const err = validateProject(editingProject.value)
  if (err) { projectErrors.value = err; return }
  projectErrors.value = ''
  const idx = profileDoc.value.doc.projects.findIndex((p) => p.name === editingProject.value.name)
  if (idx !== -1) Object.assign(profileDoc.value.doc.projects[idx], editingProject.value)
  profileDoc.value.save
    .submit()
    .then(() => {
      editingProject.value = null
      toast.success('Project updated')
    })
    .catch((e) => {
      profileDoc.value.get.submit()
      projectErrors.value = e?.message || 'Failed to update project'
    })
}

const deleteProject = (rowName) => {
  if (!profileDoc.value?.doc) return
  if (!confirm('Delete this project?')) return
  profileDoc.value.doc.projects = profileDoc.value.doc.projects.filter((p) => p.name !== rowName)
  profileDoc.value.save
    .submit()
    .then(() => {
      toast.success('Project deleted')
    })
    .catch((e) => {
      profileDoc.value.get.submit()
      toast.error(e?.message || 'Failed to delete project')
    })
}
</script>
