var LoadView = {
    emits: ['open_hash_command'],

    mounted() {
        this.$emit('open_hash_command');
    },
    
    template: `<h1>Loading file...</h1>`
};