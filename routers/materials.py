import os
import shutil
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import User, Material
from schemas import Material as MaterialSchema, MaterialCreate
from auth import get_current_active_user
from services.pdf_processor import PDFProcessor
from config import settings

router = APIRouter()

@router.post("/upload", response_model=MaterialSchema)
async def upload_material(
    file: UploadFile = File(...),
    title: str = Form(...),
    subject: str = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and process a PDF material"""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported"
        )
    
    # Check file size
    file_size = 0
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB limit"
        )
    
    # Create unique filename
    import uuid
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Process PDF
        pdf_result = PDFProcessor.extract_text_from_bytes(file_content, file.filename)
        
        if not pdf_result['success']:
            # Clean up file on processing failure
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"PDF processing failed: {pdf_result.get('error', 'Unknown error')}"
            )
        
        # Create material record
        material = Material(
            user_id=current_user.id,
            title=title,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            extracted_text=pdf_result['full_text'],
            word_count=pdf_result['statistics']['word_count'],
            estimated_reading_time=pdf_result['statistics']['estimated_reading_time'],
            difficulty_score=pdf_result['statistics']['difficulty_score'],
            subject=subject,
            content_type="pdf"
        )
        
        db.add(material)
        db.commit()
        db.refresh(material)
        
        return material
        
    except Exception as e:
        # Clean up file on any error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload: {str(e)}"
        )

@router.get("/", response_model=List[MaterialSchema])
async def get_materials(
    subject: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all materials for the current user"""
    
    query = db.query(Material).filter(Material.user_id == current_user.id)
    
    if subject:
        query = query.filter(Material.subject == subject)
    
    materials = query.order_by(Material.created_at.desc()).all()
    return materials

@router.get("/{material_id}", response_model=MaterialSchema)
async def get_material(
    material_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific material"""
    
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    return material

@router.get("/{material_id}/content")
async def get_material_content(
    material_id: int,
    section: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get material content, optionally by section"""
    
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    if section is not None:
        # Extract specific section
        sections = PDFProcessor.extract_sections(material.extracted_text)
        if section < 1 or section > len(sections):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid section number"
            )
        
        return {
            'section_number': section,
            'content': sections[section - 1]['text'],
            'word_count': sections[section - 1]['word_count'],
            'estimated_reading_time': sections[section - 1]['estimated_reading_time'],
            'total_sections': len(sections)
        }
    
    # Return full content
    sections = PDFProcessor.extract_sections(material.extracted_text)
    
    return {
        'title': material.title,
        'full_content': material.extracted_text,
        'word_count': material.word_count,
        'estimated_reading_time': material.estimated_reading_time,
        'difficulty_score': material.difficulty_score,
        'total_sections': len(sections),
        'sections': sections
    }

@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a material and its associated file"""
    
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Delete the physical file
    if os.path.exists(material.file_path):
        try:
            os.remove(material.file_path)
        except OSError as e:
            print(f"Error deleting file {material.file_path}: {e}")
    
    # Delete database record
    db.delete(material)
    db.commit()
    
    return {"message": "Material deleted successfully"}

@router.get("/{material_id}/stats")
async def get_material_stats(
    material_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a material"""
    
    material = db.query(Material).filter(
        Material.id == material_id,
        Material.user_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    # Get sections for analysis
    sections = PDFProcessor.extract_sections(material.extracted_text)
    
    # Calculate additional statistics
    text = material.extracted_text
    paragraphs = len([p for p in text.split('\n\n') if p.strip()])
    sentences = len([s for s in text.split('.') if s.strip()])
    avg_words_per_sentence = material.word_count / sentences if sentences > 0 else 0
    
    return {
        'basic_stats': {
            'word_count': material.word_count,
            'estimated_reading_time': material.estimated_reading_time,
            'difficulty_score': material.difficulty_score,
            'file_size': material.file_size
        },
        'content_structure': {
            'total_sections': len(sections),
            'paragraphs': paragraphs,
            'sentences': sentences,
            'avg_words_per_sentence': round(avg_words_per_sentence, 1)
        },
        'sections': [
            {
                'section_number': s['section_number'],
                'word_count': s['word_count'],
                'estimated_reading_time': s['estimated_reading_time']
            }
            for s in sections
        ]
    }
