from django.db import models

from deprecated_field import deprecated


class Artist(models.Model):

    # A field that migrations have not been created for
    name = deprecated(models.CharField(max_length=256))


class Album(models.Model):
    # A non-relational deprecated field.
    title = deprecated(models.CharField(max_length=256))

    # A foreign that's deprecated.
    artist = deprecated(
        models.ForeignKey(Artist, related_name="albums", on_delete=models.CASCADE)
    )


class Genre(models.Model):
    # A deprecated field that does not exist in the database.
    name = deprecated(models.CharField())
