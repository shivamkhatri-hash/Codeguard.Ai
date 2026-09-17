
# Code_Analysis_Agent_frontend
=======
# Smart Code Inspection Platform — Frontend

Initial development phase: **Code Submission + Validation**.

This frontend follows the project document's Milestone 1 requirement to support direct code paste/file upload for Python and Java with syntax validation. fileciteturn0file0L53-L62

## Stack

- React + Vite
- JavaScript
- Tailwind CSS
- Prism.js + react-simple-code-editor
- Lucide icons

## Run

```bash
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173

Set the backend URL in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Backend endpoints

### Submit
`POST /api/code/submit`

JSON:

```json
{
  "language": "python",
  "code": "print('Hello World')"
}
```

### Upload
`POST /api/code/upload`

Multipart form field:

`file`

The frontend also reads `.py` and `.java` files locally so the selected source is immediately displayed in the editor. The upload request is made separately to the backend.

## Expected response

The result card accepts common field names:

```json
{
  "analysis_id": "ABC123",
  "language": "python",
  "syntax_validation": "Valid",
  "status": "Submitted",
  "message": "Code submitted successfully"
}
```

It also tolerates `analysisId`, `syntaxValidation`, `syntax`, `id`, and `detail/message` style backend responses.

## Important scope

Not implemented in this phase:

- AI agents
- LangGraph
- RAG
- Chatbot
- Security analysis
- PDF reports
- Authentication
- GitHub integration
- Advanced dashboard

These belong to later project milestones.

