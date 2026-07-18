# HiHi — Real-Time Chat Application

## Overview

HiHi is a full-stack, real-time messaging application built to deepen practical skills in backend architecture, real-time systems, and cross-platform mobile development. The project follows the core communication patterns found in production messaging apps — one-to-one chat, group conversations, presence indicators, and file sharing — implemented from the ground up rather than relying on a pre-built chat SDK.

The goal of this project is craft mastery: understanding *why* each architectural decision is made, not just shipping a working demo.

## Tech Stack

**Backend**
- **Python / Flask** — application server, structured using the application factory pattern with blueprints
- **Flask-SocketIO** — real-time, bidirectional communication (messaging, typing indicators, presence)
- **MongoDB (Atlas)** — primary data store, chosen for its natural fit with document-shaped chat data (messages, conversations)
- **Flask-Bcrypt** — password hashing
- **PyJWT** — stateless authentication via JSON Web Tokens
- **Flask-CORS** — cross-origin support for the Flutter client

**Frontend**
- **Flutter** — cross-platform mobile client (Android APK as primary target)
- **Provider** — state management
- **socket_io_client** — real-time client connection to the backend
- **flutter_secure_storage** — secure JWT storage on-device

## Architecture

The backend follows a modular, blueprint-based structure separating concerns into distinct domains:
