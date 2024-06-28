<template>
  <div class="flex">
    <SideNavbar :class="showNav ? 'z-50 block mt-[55px]' : 'hidden md:block'"/>
    <div class="w-full md:ml-[220px]">
      <HeaderWithNav @toggleSidebar="($event) => (showNav = $event)" />
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
            <div
                class="top-3 right-3 absolute flex gap-1"
            >
            <FileUploader
              :fileTypes="'image/*'"
              :validateFile="validateFile"
              @success="(file) => setBannerImage(file)"
            >
              <template
                v-slot="{ file, progress, error, uploading, openFileSelector }"
              >
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
                @click="setBannerImage({file_url: ''})"
            />
            </div>
          </div>
          <div class="z-10 w-fit relative -mt-12 mx-6">
            <img
              class="aspect-square border-4 border-white rounded w-28"
              :src="profile.data.profile_photo"
              alt="Profile Photo"
            />
            <FileUploader
              class="top-3 right-3 absolute"
              :fileTypes="'image/*'"
              :validateFile="validateFile"
              @success="(file) => setProfileImage(file)"
            >
              <template
                v-slot="{ file, progress, error, uploading, openFileSelector }"
              >
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
              v-model="profile_dict.email"
              placeholder="Enter your email"
              disabled
            />
            <FormControl
              label="Username &ast;"
              v-model="profile_dict.username"
              placeholder="Enter your username"
            />
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
            <div class="col-span-2 text-sm text-gray-600">Enter the complete links to your social, including <code>https://</code></div>
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
                    @click="updateProfile()"
                />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import HeaderWithNav from '@/components/HeaderWithNav.vue'
import SideNavbar from '@/components/NewAppSidebar.vue'
import TextEditor from '@/components/TextEditor.vue'
import { createResource, FileUploader, Switch, FormControl, ErrorMessage } from 'frappe-ui'
import { inject, reactive, ref } from 'vue'
import { toast } from 'vue-sonner'

const session = inject('$session')

const showNav = ref(false)

const profile_dict = reactive({
    full_name: '',
    email: '',
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
  url: 'fossunited.fossunited.utils.get_foss_profile',
  makeParams() {
    return {
      email: session.user,
    }
  },
  auto: true,
  onSuccess(data){
    Object.keys(profile_dict).forEach(key => {
      profile_dict[key] = data[key]
    })
  }
})

const validateFile = (file) => {
  let extn = file.name.split('.').pop().toLowerCase()
  if (!['png', 'jpg'].includes(extn)) {
    return 'Only PNG and JPG images are allowed'
  }
}

const setBannerImage = (file) => {
    createResource({
        url: 'frappe.client.set_value',
        makeParams(){
            return{
                doctype: 'FOSS User Profile',
                name: profile.data.name,
                fieldname: 'cover_image',
                value: file.file_url
            }
        },
        auto: true,
        onSuccess(){
            if (file.file_url){
                toast.success('Banner Image Updated')
            } else {
                toast.success('Banner Image Removed')
            }
            profile.fetch()
        }
    })
}

const setProfileImage = (file) => {
    createResource({
        url: 'frappe.client.set_value',
        makeParams(){
            return{
                doctype: 'FOSS User Profile',
                name: profile.data.name,
                fieldname: 'profile_photo',
                value: file.file_url
            }
        },
        auto: true,
        onSuccess(){
            toast.success('Profile Image Updated')
            profile.fetch()
        }
    })
}

const toggleProfilePrivacy = () => {
    createResource({
        url: 'frappe.client.set_value',
        makeParams(){
            return{
                doctype: 'FOSS User Profile',
                name: profile.data.name,
                fieldname: 'is_private',
                value: profile.data.is_private
            }
        },
        auto: true,
        onSuccess(){
            if (profile.data.is_private){
                toast.info('Profile is now private')
            } else {
                toast.info('Profile is now public')
            }
            profile.fetch()
        }
    })
}

const updateErrors = ref('')

const updateProfileErrors = () => {
    const errors = []

    if (!profile_dict.full_name){
        errors.push('Full Name is required')
    }
    if (!profile_dict.username){
        errors.push('Username is required')
    }
    if (!profile_dict.email){
        errors.push('Email is required')
    }

    return errors
}

const updateProfile = () => {
    const errors = updateProfileErrors()
    if (errors.length){
        updateErrors.value = errors.join(', ')
        return
    }
    else {
        updateErrors.value = ''
    }

    createResource({
        url: 'frappe.client.set_value',
        makeParams(){
            return{
                doctype: 'FOSS User Profile',
                name: profile.data.name,
                fieldname: profile_dict
            }
        },
        auto: true,
        onSuccess(){
            toast.success('Profile Updated Successfully')
            profile.fetch()
        },
        onError(){
            toast.error('Error updating profile')
        }
    })
}
</script>
