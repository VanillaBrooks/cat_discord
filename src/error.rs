/// root: the type we are converting away from
/// destination_enum: type converting to
/// path: path in destination we do to
macro_rules! from {
    ($root:path, $destination_enum:ident :: $path_:ident) => {
        impl From<$root> for $destination_enum {
            fn from(e: $root) -> Self {
                $destination_enum::$path_(e)
            }
        }
    };
}

#[derive(Debug)]
pub enum Error {
    Files(FilesError),
    Picture(PictureError),
    Discord(DiscordError),
}

#[derive(Debug)]
pub enum FilesError {
    IoError(std::io::Error),
    SerdeJson(serde_json::Error),
    Reqwest(reqwest::Error),
}

#[derive(Debug)]
pub enum PictureError {
    IoError(std::io::Error),
    Reqwest(reqwest::Error),
    NoValidPictures,
}

#[derive(Debug)]
pub enum DiscordError {
    IoError(std::io::Error),
    SerdeJson(serde_json::Error),
    Serenity(serenity::Error),
}

from! {std::io::Error, FilesError::IoError}
from! {reqwest::Error, FilesError::Reqwest}
from! {serde_json::Error, FilesError::SerdeJson}

from! {std::io::Error, PictureError::IoError}
from! {reqwest::Error, PictureError::Reqwest}

from! {std::io::Error, DiscordError::IoError}
from! {serde_json::Error, DiscordError::SerdeJson}
from! {serenity::Error, DiscordError::Serenity}

from! {FilesError, Error::Files}
from! {PictureError, Error::Picture}
from! {DiscordError, Error::Discord}
