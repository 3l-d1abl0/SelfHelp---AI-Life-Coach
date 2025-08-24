<script>
	import newLogo from '$assets/yellow-halo.png';
	import { goto } from '$app/navigation';
	
	function startLifeCoaching() {
		goto('/meeting/new');
	}
</script>

<svelte:head>
	<title>AI Life Coach - Transform Your Life</title>
</svelte:head>

<div class="home-screen">
	<div class="floating-elements">
		<div class="float-element float-1"></div>
		<div class="float-element float-2"></div>
		<div class="float-element float-3"></div>
		<div class="float-element float-4"></div>
	</div>
	
	<div class="home-content">
		<div class="hero-section">
			<div class="hero-icon">
				<img class="new-logo" src={newLogo} alt="AI Life Coach" />
			</div>
			
			<div class="title-container">
				<h1>AI Life Coach</h1>
				<div class="title-accent"></div>
			</div>
			<p class="hero-subtitle">Unlock your potential with personalized AI guidance that adapts to your unique journey</p>
			
			<div class="features">
				<div class="feature">
					<div class="feature-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</div>
					<h3>Emotionally Intelligent AI Support</h3>
					<p>Your AI mentor understands not just your words, but your feelings — offering empathetic, personalized guidance tailored to your emotional needs.</p>
				</div>
				
				<div class="feature">
					<div class="feature-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
						</svg>
					</div>
					<h3>Reflect, Learn, and Grow</h3>
					<p>Gain AI-powered insights to understand your patterns, strengths, and areas for growth.</p>
				</div>
				
				<div class="feature">
					<div class="feature-icon">
						<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
							<circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
							<path d="M12 1v6m0 6v6m11-7h-6m-6 0H1" stroke="currentColor" stroke-width="2"/>
						</svg>
					</div>
					<h3>Balanced Life, Fulfilled You</h3>
					<p>Get tailored advice for career, relationships, and wellness—all in one place—so you can thrive in every aspect of life.</p>
				</div>
			</div>
			<div class="cta-section">
				<button class="start-btn" on:click={startLifeCoaching}>
					Begin Your Transformation
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
						<path d="M5 12l5 5L20 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
					</svg>
				</button>
				
				<p class="cta-note">Start your personalized journey to a better you</p>
			</div>
			
		</div>
	</div>
</div>

<style>
	.home-screen {
		min-height: 100vh;
		/*background-image: linear-gradient(146deg, rgba(44, 35, 109, 0.5) 0%, rgba(44, 35, 109, 0.5) 14.286%,rgba(64, 54, 108, 0.5) 14.286%, rgba(64, 54, 108, 0.5) 28.572%,rgba(83, 72, 106, 0.5) 28.572%, rgba(83, 72, 106, 0.5) 42.858%,rgba(103, 91, 105, 0.5) 42.858%, rgba(103, 91, 105, 0.5) 57.144%,rgba(123, 110, 103, 0.5) 57.144%, rgba(123, 110, 103, 0.5) 71.43%,rgba(142, 128, 102, 0.5) 71.43%, rgba(142, 128, 102, 0.5) 85.716%,rgba(162, 147, 100, 0.5) 85.716%, rgba(162, 147, 100, 0.5) 100.002%),linear-gradient(349deg, rgb(203, 4, 7) 0%, rgb(203, 4, 7) 14.286%,rgb(178, 9, 6) 14.286%, rgb(178, 9, 6) 28.572%,rgb(152, 13, 5) 28.572%, rgb(152, 13, 5) 42.858%,rgb(127, 18, 4) 42.858%, rgb(127, 18, 4) 57.144%,rgb(101, 22, 3) 57.144%, rgb(101, 22, 3) 71.43%,rgb(76, 27, 2) 71.43%, rgb(76, 27, 2) 85.716%,rgb(50, 31, 1) 85.716%, rgb(50, 31, 1) 100.002%);*/
		color: white;
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20px;
		position: relative;
		overflow: hidden;
	}
	
	.floating-elements {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		pointer-events: none;
		z-index: 1;
	}
	
	.float-element {
		position: absolute;
		border-radius: 50%;
		background: rgba(255, 255, 255, 0.1);
		backdrop-filter: blur(10px);
		animation: floatAround 20s infinite linear;
	}
	
	.float-1 {
		width: 100px;
		height: 100px;
		top: 10%;
		left: 10%;
		animation-delay: 0s;
	}
	
	.float-2 {
		width: 150px;
		height: 150px;
		top: 60%;
		right: 15%;
		animation-delay: -5s;
	}
	
	.float-3 {
		width: 80px;
		height: 80px;
		bottom: 20%;
		left: 20%;
		animation-delay: -10s;
	}
	
	.float-4 {
		width: 120px;
		height: 120px;
		top: 30%;
		right: 30%;
		animation-delay: -15s;
	}
	
	@keyframes floatAround {
		0% {
			transform: translateY(0px) rotate(0deg);
		}
		33% {
			transform: translateY(-30px) rotate(120deg);
		}
		66% {
			transform: translateY(20px) rotate(240deg);
		}
		100% {
			transform: translateY(0px) rotate(360deg);
		}
	}
	
	.home-content {
		max-width: 1000px;
		width: 100%;
		text-align: center;
		position: relative;
		z-index: 2;
	}
	
	.hero-section {
		padding: 60px 40px;
	}
	
	.hero-icon {
		margin-bottom: 32px;
		animation: float 3s ease-in-out infinite;
		transform: scale(1.2);
	}
	
	@keyframes float {
		0%, 100% {
			transform: translateY(0px) scale(1.2);
		}
		50% {
			transform: translateY(-15px) scale(1.3);
		}
	}
	
	.new-logo {
		height: 120px;
		filter: drop-shadow(0 10px 30px rgba(255, 255, 255, 0.3));
	}
	
	.title-container {
		position: relative;
		display: inline-block;
		margin-bottom: 24px;
	}
	
	.title-accent {
		position: absolute;
		bottom: -10px;
		left: 50%;
		transform: translateX(-50%);
		width: 100%;
		height: 4px;
		background: linear-gradient(90deg, #4ade80, #ec4899);
		border-radius: 2px;
		/*animation: pulse 2s ease-in-out infinite;*/
	}
	
	@keyframes pulse {
		0%, 100% {
			opacity: 0.7;
			transform: translateX(-50%) scaleX(1);
		}
		50% {
			opacity: 1;
			transform: translateX(-50%) scaleX(1.1);
		}
	}
	
	h1 {
		font-size: 4.5rem;
		margin: 0;
		font-weight: 900;
		background: linear-gradient(135deg, #ffffff 0%, #fff3e0 50%, #e3f2fd 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		line-height: 1.1;
		text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
		letter-spacing: -2px;
	}
	
	.hero-subtitle {
		font-size: 1.4rem;
		color: rgba(255, 255, 255, 0.9);
		margin-bottom: 60px;
		max-width: 650px;
		margin-left: auto;
		margin-right: auto;
		line-height: 1.7;
		font-weight: 300;
		text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
	}
	
	.features {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 30px;
		margin-bottom: 80px;
		perspective: 1000px;
	}
	
	.feature {
		background: rgba(255, 255, 255, 0.15);
		border: 1px solid rgba(255, 255, 255, 0.2);
		border-radius: 20px;
		padding: 40px 28px;
		backdrop-filter: blur(20px);
		transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
		position: relative;
		overflow: hidden;
	}
	
	.feature::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
		transition: left 0.6s;
	}
	
	.feature:hover::before {
		left: 100%;
	}
	
	.feature:hover {
		transform: translateY(-5px) rotateX(2deg);
		border-color: rgba(255, 255, 255, 0.4);
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
		background: rgba(255, 255, 255, 0.2);
	}
	
	.feature-icon {
		width: 70px;
		height: 70px;
		background: linear-gradient(135deg, #4ade80, #22d3ee);
		border-radius: 50%;
		display: flex;
		align-items: center;
		justify-content: center;
		margin: 0 auto 24px;
		color: white;
		box-shadow: 0 10px 30px rgba(74, 222, 128, 0.3);
		transition: all 0.3s ease;
	}
	
	.feature:hover .feature-icon {
		transform: scale(1.1) rotate(10deg);
		box-shadow: 0 15px 40px rgba(74, 222, 128, 0.4);
	}
	
	.feature h3 {
		font-size: 1.4rem;
		margin-bottom: 16px;
		color: #ffffff;
		font-weight: 700;
		text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
	}
	
	.feature p {
		color: rgba(255, 255, 255, 0.8);
		line-height: 1.6;
		margin: 0;
		font-weight: 300;
	}
	
	.cta-section {
		margin-top: 80px;
	}
	
	.start-btn {
		display: inline-flex;
		align-items: center;
		gap: 16px;
		padding: 24px 48px;
		background: linear-gradient(135deg, #4ade80 0%, #22d3ee 50%, #a855f7 100%);
		
		background: linear-gradient(90deg, #621e40 0%, #792828 100%);
		color: white;
		border: none;
		border-radius: 50px;
		font-size: 1.3rem;
		font-weight: 800;
		cursor: pointer;
		transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
		box-shadow: 0 15px 35px rgba(15, 15, 15, 0.4);
		text-transform: none;
		letter-spacing: 0.5px;
		position: relative;
		overflow: hidden;
	}
	
	.start-btn::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
		transition: left 0.6s;
	}
	
	.start-btn:hover::before {
		left: 100%;
	}
	
	.start-btn:hover {
		transform: translateY(-5px) scale(1.05);
		box-shadow: 0 20px 50px rgba(15, 15, 15, 0.5);
		background: linear-gradient(135deg, #321F01 0%, #7F1204 50%, #CB0407 100%);
		
		
	}
	
	.start-btn:active {
		transform: translateY(-2px) scale(1.02);
	}
	
	.cta-note {
		margin-top: 24px;
		color: rgba(255, 255, 255, 0.7);
		font-size: 1.1rem;
		font-style: italic;
		font-weight: 300;
	}
	
	@media (max-width: 1024px) and (min-width: 769px) {
		.features {
			grid-template-columns: repeat(3, 1fr);
			gap: 20px;
		}
		
		.feature {
			padding: 30px 20px;
		}
	}
	
	@media (max-width: 768px) {
		.floating-elements {
			display: none;
		}
		
		.hero-section {
			padding: 40px 20px;
		}
		
		.new-logo {
			height: 100px;
		}
		
		h1 {
			font-size: 3.5rem;
			letter-spacing: -1px;
		}
		
		.hero-subtitle {
			font-size: 1.2rem;
			margin-bottom: 40px;
			max-width: 500px;
		}
		
		.features {
			grid-template-columns: 1fr;
			gap: 20px;
			margin-bottom: 60px;
		}
		
		.feature {
			padding: 32px 24px;
		}
		
		.feature-icon {
			width: 60px;
			height: 60px;
		}
		
		.start-btn {
			padding: 20px 40px;
			font-size: 1.2rem;
			gap: 12px;
		}
		
		.cta-section {
			margin-top: 60px;
		}
	}
	
	@media (max-width: 480px) {
		.hero-section {
			padding: 30px 15px;
		}
		
		.new-logo {
			height: 80px;
		}
		
		h1 {
			font-size: 2.8rem;
			letter-spacing: -1px;
		}
		
		.hero-subtitle {
			font-size: 1.1rem;
			max-width: 400px;
		}
		
		.feature {
			padding: 28px 20px;
		}
		
		.feature-icon {
			width: 50px;
			height: 50px;
		}
		
		.feature h3 {
			font-size: 1.2rem;
		}
		
		.start-btn {
			padding: 18px 36px;
			font-size: 1.1rem;
			gap: 10px;
		}
		
		.cta-note {
			font-size: 1rem;
		}
	}
</style>