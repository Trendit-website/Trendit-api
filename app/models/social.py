'''
This module defines the Social Links model for the database.

It includes fields for the user's social media profile links

@author Emmanuel Olowu
@link: https://github.com/zeddyemy
@package Trendit³
'''

from enum import Enum

from ..extensions import db

social_media_platforms = ["facebook", "instagram", "x", "tiktok", "threads"]

class SocialLinkStatus(Enum):
    IDLE = 'idle'
    PENDING = 'pending'
    VERIFIED = 'verified'
    REJECTED = 'rejected'

class SocialMediaProfile(db.Model):
    
    id = db.Column(db.Integer(), primary_key=True)
    platform = db.Column(db.String(200), nullable=True) # facebook, instagram, tiktok, x, threads, youtube
    link = db.Column(db.String(200), default="", nullable=True)
    status = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False,)
    trendit3_user = db.relationship('Trendit3User', backref=db.backref('social_media_profiles', lazy='dynamic'))
    
    def __repr__(self):
        return f'< primary ID: {self.id}, platform: {self.platform}, status: {self.status} >'
    
    @classmethod
    def add_profile(cls, trendit3_user, platform, link, status=SocialLinkStatus.PENDING, commit=True):
        profile = cls(trendit3_user=trendit3_user, platform=platform, link=link, status=status)
        
        db.session.add(profile)
        
        if commit:
            db.session.commit()
        
        return profile
    
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self, commit=True):
        db.session.delete(self)
        
        if commit:
            db.session.commit()
    
    def to_dict(self):
        return {
            'platform': self.platform,
            'link': self.link,
            'status': str(self.status.value)
        }


class SocialLinks(db.Model):
    
    id = db.Column(db.Integer(), primary_key=True)
    google_id = db.Column(db.String(200), default="", nullable=True)
    google_verified = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    facebook_id = db.Column(db.String(200), default="", nullable=True)
    facebook_verified = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    instagram_id = db.Column(db.String(200), default="", nullable=True)
    instagram_verified = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    tiktok_id = db.Column(db.String(200), default="", nullable=True)
    tiktok_verified = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    x_id = db.Column(db.String(200), default="", nullable=True)
    x_verified = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    threads_id = db.Column(db.String(200), default="", nullable=True)
    threads_verified = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    # youtube_id = db.Column(db.String(200), default="", nullable=True)
    # youtube_verified = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    # spotify_id = db.Column(db.String(200), default="", nullable=True)
    # spotify_verified = db.Column(db.Enum(SocialLinkStatus), default=SocialLinkStatus.IDLE)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False,)
    trendit3_user = db.relationship('Trendit3User', back_populates="social_links")
    
    def __repr__(self):
        return f'< primary ID: {self.id}, google_id: {self.google_id}, facebook_id: {self.facebook_id} >'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def to_dict(self):
        return {
            'google_id': self.google_id,
            'google_verified': str(self.google_verified),
            'facebook_id': self.facebook_id,
            'facebook_verified': str(self.facebook_verified),
            'instagram_id': self.instagram_id,
            'instagram_verified': str(self.instagram_verified),
            'tiktok_id': self.tiktok_id,
            'tiktok_verified': str(self.tiktok_verified),
            'x_id': self.x_id,
            'x_verified': str(self.x_verified),
            'threads_id': self.threads_id,
            'threads_verified': str(self.threads_verified),
            'youtube_id': self.youtube_id,
            'youtube_verified': str(self.youtube_verified),
            'spotify_id': self.spotify_id,
            'spotify_verified': str(self.spotify_verified),
        }


class SocialIDs(db.Model):
    
    id = db.Column(db.Integer(), primary_key=True)
    google_id = db.Column(db.String(200), default="", nullable=True)
    facebook_id = db.Column(db.String(200), default="", nullable=True)
    instagram_id = db.Column(db.String(200), default="", nullable=True)
    tiktok_id = db.Column(db.String(200), default="", nullable=True)
    x_id = db.Column(db.String(200), default="", nullable=True)
    
    trendit3_user_id = db.Column(db.Integer, db.ForeignKey('trendit3_user.id', ondelete='CASCADE'), nullable=False,)
    trendit3_user = db.relationship('Trendit3User', back_populates="social_ids")
    
    def __repr__(self):
        return f'< primary ID: {self.id}, google_id: {self.google_id}, facebook_id: {self:facebook_id} >'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def to_dict(self):
        return {
            'google_id': self.google_id,
            'facebook_id': self.facebook_id,
            'instagram_id': self.instagram_id,
            'tiktok_id': self.tiktok_id,
            'x_id': self.x_id,
        }






class SocialMediaPlatform(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(200), unique=True, nullable=True) # facebook, instagram, tiktok, x, threads, youtube
    
    def __repr__(self):
        return f'< primary ID: {self.id}, name: {self.name} >'
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }