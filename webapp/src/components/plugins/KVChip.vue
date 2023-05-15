<template>
    <div>
        <v-chip :label="label" :small="small" :x-small="xSmall" :large="large" :x-range="xLarge" class="rounded-r-0 mr-0"
            :color="nameColor" >{{ name }}</v-chip>
        <v-chip :small="small" :x-small="xSmall" :large="large" :x-range="xLarge" class="rounded-l-0  ml-0"
            :color="valueColor" >{{ value }}</v-chip>
    </div>
</template>

<script>

export default {
    props: {
        name: String,
        value: [String, Number],
        nameColor: {
            type: String, default: 'primary'
        },
        label: { type: Boolean, default: false },
        valueColor: { type: String, default: 'info' },
        small: { type: Boolean, default: false },
        xSmall: { type: Boolean, default: false },
        large: { type: Boolean, default: false },
        xLarge: { type: Boolean, default: false },
    },

};


</script>