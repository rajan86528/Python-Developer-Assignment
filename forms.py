from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from database import get_session, Form, Field as FormField, Submission
from auth import authenticated_user

forms_router = APIRouter()

class FieldRequest(BaseModel):
    field_id: str
    type: str
    label: str
    required: bool

class FormRequest(BaseModel):
    title: str
    description: str
    fields: list[FieldRequest]

class SubmissionRequest(BaseModel):
    responses: list[dict]

# Create Form
@forms_router.post("/create")
async def create_form(form: FormRequest, session: AsyncSession = Depends(get_session), user_id: int = Depends(authenticated_user)):
    new_form = Form(title=form.title, description=form.description, owner_id=user_id)
    session.add(new_form)
    await session.commit()
    for field in form.fields:
        new_field = FormField(form_id=new_form.id, **field.dict())
        session.add(new_field)
    await session.commit()
    return {"message": "Form created successfully", "form_id": new_form.id}

# Delete Form
@forms_router.delete("/delete/{form_id}")
async def delete_form(form_id: int, session: AsyncSession = Depends(get_session), user_id: int = Depends(authenticated_user)):
    form = await session.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")

    if form.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this form")

    # Delete associated fields
    result = await session.execute(select(FormField).filter(FormField.form_id == form_id))
    fields = result.scalars().all()
    for field in fields:
        await session.delete(field)

    result = await session.execute(select(Submission).filter(Submission.form_id == form_id))
    submissions = result.scalars().all()
    for submission in submissions:
        await session.delete(submission)

    await session.delete(form)
    await session.commit()

    return {"message": "Form and associated fields/submissions deleted"}

# Get All Forms
@forms_router.get("/")
async def get_forms(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Form))
    forms = result.scalars().all()
    return {"forms": forms}

# Get Single Form
@forms_router.get("/{form_id}")
async def get_single_form(form_id: int, session: AsyncSession = Depends(get_session)):
    form = await session.get(Form, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    
    result = await session.execute(select(FormField).filter(FormField.form_id == form_id))
    fields = result.scalars().all()

    return {
        "id": form.id,
        "title": form.title,
        "description": form.description,
        "fields": [{"field_id": field.field_id, "type": field.type, "label": field.label, "required": field.required} for field in fields]
    }

# Submit Form
@forms_router.post("/submit/{form_id}")
async def submit_form(form_id: int, submission: SubmissionRequest, session: AsyncSession = Depends(get_session)):
    for response in submission.responses:
        new_submission = Submission(form_id=form_id, field_id=response["field_id"], value=response["value"])
        session.add(new_submission)
    await session.commit()
    return {"message": "Form submitted successfully"}

# Get Form Submissions with Pagination
@forms_router.get("/submissions/{form_id}")
async def get_form_submissions(
    form_id: int, 
    page: int = 1, 
    limit: int = 10, 
    session: AsyncSession = Depends(get_session)
):
    offset = (page - 1) * limit

    result = await session.execute(
        select(Submission)
        .filter(Submission.form_id == form_id)
        .offset(offset)
        .limit(limit)
    )
    submissions = result.scalars().all()

    total_count_result = await session.execute(
        select(func.count()).filter(Submission.form_id == form_id)
    )
    total_count = total_count_result.scalar() 

    return {
        "total_count": total_count,
        "page": page,
        "limit": limit,
        "submissions": [
            {
                "submission_id": submission.id,
                "data": {
                    submission.field_id: submission.value
                    for submission in submissions if submission.form_id == form_id
                }
            } 
            for submission in submissions
        ]
    }