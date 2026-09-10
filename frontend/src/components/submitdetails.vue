<!-- src/components/SubmitDetails.vue -->
<script setup>
import { ref } from 'vue'

const username = ref('')
const gameId = ref('')
const responseMessage = ref('')

const sendData = async () => {
  try {
    // 🟢 Precision target pointing to your exact live Flask API endpoint
    const response = await fetch('https://onrender.com', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json' 
      },
      body: JSON.stringify({
        username: username.value,
        gameId: gameId.value
      })
    })

    const data = await response.json()
    
    // Updates your UI with the success or error message sent by Flask
    responseMessage.value = data.message
    
  } catch (error) {
    console.error("Connection failed:", error)
    responseMessage.value = "Could not reach the server."
  }
}

</script>

<template>
  <div class="form-container">
    <h2>Player Registration</h2>
    <h2>This is fucking goat</h2>
    <input v-model="username" placeholder="Enter Username" />
    <input v-model="gameId" placeholder="Enter Game ID" />
    <button @click="sendData">Submit Entry</button>
    <p v-if="responseMessage" class="msg">{{ responseMessage }}</p>
  </div>
</template>

<style scoped>
.form-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}
input, button {
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
button {
  background-color: #42b883;
  color: white;
  cursor: pointer;
  font-weight: bold;
}
.msg {
  text-align: center;
  color: #2c3e50;
}
</style>
