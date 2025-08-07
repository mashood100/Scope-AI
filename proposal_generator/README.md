# Proposal Generator API

This Django app provides AI-powered job proposal generation based on job descriptions.

## Features

- Generate professional freelance proposals for UpWork gigs
- Store and retrieve generated proposals
- Extract job metadata automatically
- Uses OpenAI GPT for intelligent proposal generation

## API Endpoints

### 1. Generate Proposal

**POST** `/proposals/api/generate/`

Generate a new proposal based on a job description.

**Request Body:**

```json
{
  "job_description": "Your job description here...",
  "user_id": "user123"
}
```

**Response:**

```json
{
  "success": true,
  "proposal_id": 1,
  "generated_proposal": "Hey there! I'm excited about your project...",
  "job_title": "Extracted job title",
  "created_at": "2024-01-15T10:30:00Z",
  "message": "Proposal generated successfully"
}
```

### 2. Get User Proposals

**GET** `/proposals/api/user/{user_id}/`

Retrieve all proposals for a specific user with pagination.

**Response:**

```json
{
  "count": 25,
  "next": "http://localhost:8000/proposals/api/user/user123/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "job_title": "Web Development Project",
      "job_description": "Looking for a developer to build...",
      "generated_proposal": "Hey there! I'm excited about...",
      "budget_range": "$500-1000",
      "project_duration": "2 weeks",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

### 3. Get Proposal Details

**GET** `/proposals/api/detail/{proposal_id}/`

Get detailed information about a specific proposal.

**Response:**

```json
{
  "id": 1,
  "job_title": "Web Development Project",
  "job_description": "Full job description...",
  "generated_proposal": "Complete generated proposal...",
  "budget_range": "$500-1000",
  "project_duration": "2 weeks",
  "user_id": "user123",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## AI Prompt

The API uses this specific prompt for generating proposals:

> "Write a straightforward and to-the-point bid proposal to this UpWork gig pasted below in 150 words as a freelancer and discuss every aspect of this job technically as a freelancer in informal language. Ask a question about the project in the end."

## Setup Requirements

1. **OpenAI API Key**: Set your OpenAI API key in the `dev.env` file:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Database Migration**: Run migrations to create the required tables:

   ```bash
   python manage.py makemigrations proposal_generator
   python manage.py migrate
   ```

3. **Install Dependencies**: Make sure python-dotenv is installed:
   ```bash
   pip install python-dotenv
   ```

## Error Handling

The API includes comprehensive error handling for:

- Missing required fields
- Invalid job descriptions (minimum 50 characters)
- OpenAI API failures
- Database errors

All errors return appropriate HTTP status codes and descriptive error messages.

## Usage Example

```bash
# Generate a proposal
curl -X POST http://localhost:8000/proposals/api/generate/ \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "I need a Django developer to build a REST API for my e-commerce platform. The API should handle user authentication, product management, and order processing. Budget is $800-1200.",
    "user_id": "freelancer123"
  }'

# Get user proposals
curl http://localhost:8000/proposals/api/user/freelancer123/

# Get specific proposal
curl http://localhost:8000/proposals/api/detail/1/
```
