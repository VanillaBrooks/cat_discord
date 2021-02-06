mod discord;
mod error;
mod files;
mod picture;

#[tokio::main(flavor = "current_thread")]
async fn main() {
    let api = files::Api::new();

    let prev = picture::get_previous_pictures();
    let x = discord::start_bot(prev, api).await;
    #[allow(unused_must_use)]
    dbg! {&x};
}
