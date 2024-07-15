export const truncateProjectTitle = (title, len) => {

    return title.length > len ? title.substring(0, len) + "..." : title
    }
