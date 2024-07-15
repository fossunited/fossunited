export const truncateStr = (title, len) => {

    return title.length > len ? title.substring(0, len) + "..." : title
    }
