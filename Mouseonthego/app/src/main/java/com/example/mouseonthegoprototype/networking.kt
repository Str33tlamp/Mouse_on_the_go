package com.example.mouseonthegoprototype

import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress

fun isServerReachable(serverIp: String, serverPort: Int, timeout: Int = 3000): Boolean {
    return try {
        val socket = DatagramSocket()
        socket.soTimeout = timeout
        val testMessage = "ping"
        val buffer = testMessage.toByteArray()
        val address = InetAddress.getByName(serverIp)
        val packet = DatagramPacket(buffer, buffer.size, address, serverPort)
        socket.send(packet)
        val responseBuffer = ByteArray(256)
        val responsePacket = DatagramPacket(responseBuffer, responseBuffer.size)
        socket.receive(responsePacket) // Throws timeout exception if no response

        val response = String(responsePacket.data, 0, responsePacket.length).trim()
        socket.close()
        response == "pong"
    } catch (e: Exception) {
        //e.printStackTrace()
        false
    }
}

fun sendSignalToServer(message: String, curIp: String, curPort: Int) {
    try {
        val socket = DatagramSocket()
        val buffer = message.toByteArray()
        val address = InetAddress.getByName(curIp)
        val packet = DatagramPacket(buffer, buffer.size, address, curPort)
        socket.send(packet)
        socket.close()
    } catch (e: Exception) {
        //e.printStackTrace()
    }
}

fun requestStringList(serverIp: String, serverPort: Int): Array<String> {
    return try {
        val socket = DatagramSocket()
        val packet = DatagramPacket("request_list".toByteArray(), "request_list".length, InetAddress.getByName(serverIp), serverPort)
        socket.send(packet)

        val responseBuffer = ByteArray(4096)
        val responsePacket = DatagramPacket(responseBuffer, responseBuffer.size)
        socket.soTimeout = 5000
        socket.receive(responsePacket)

        val response = String(responsePacket.data, 0, responsePacket.length).trim()
        socket.close()
        response.split(",").map { it.trim() }.toTypedArray()
    } catch (e: Exception) {
        //e.printStackTrace()
        throw e // Rethrow the exception to handle it in the calling thread
    }
}
